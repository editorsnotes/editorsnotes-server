import json

from pyelasticsearch.exceptions import ElasticHttpNotFoundError
from rest_framework.renderers import JSONRenderer

from django.apps import apps

from ..utils import make_dummy_request
from . import mappings


DEFINED_TYPES = (
    (
        'Note',
        'serialized.title',
        ['serialized.title', 'serialized.markup_html']
    ),
    (
        'Topic',
        'serialized.preferred_name',
        ['serialized.preferred_name', 'serialized.markup_html']
    ),
    (
        'Document',
        'serialized.description',
        ['serialized.description']
    )
)


class DocumentTypeConfig(object):
    def __init__(self, es, index_name, model_name, display_field,
                 highlight_fields=None):

        from editorsnotes.api import serializers
        main = apps.get_app_config('main')

        self.es = es
        self.index_name = index_name
        self.model = main.get_model(model_name)
        self.doctype = getattr(mappings, '{}DocType'.format(model_name))
        self.serializer = getattr(
            serializers, '{}Serializer'.format(model_name))

        self.highlight_fields = highlight_fields or []

    @property
    def type_label(self):
        return self.doctype._doc_type.name

    @property
    def type_mapping(self):
        return self.doctype._doc_type.mapping.to_dict()

    def clear(self):
        try:
            self.es.delete_all(self.index_name, self.type_label)
        except ElasticHttpNotFoundError:
            pass

    def data_from_object(self, obj, request=None):
        request = request or make_dummy_request()

        if not hasattr(obj, '_rest_serialized'):
            serializer = self.serializer(obj, context={'request': request})
            json_data = json.loads(JSONRenderer().render(serializer.data))
            obj._rest_serialized = json_data
        else:
            json_data = obj._rest_serialized.copy()
            json_data.pop('_embedded', None)

        data = {
            'id': obj.id,
            'serialized': json_data,
            'display_url': request.build_absolute_uri(obj.get_absolute_url()),
            'display_title': obj.as_text()
        }

        return data

    def get_object(self, instance=None, pk=None):
        if pk is None and instance is None:
            raise ValueError('Provide either a pk or instance to update.')
        obj = instance or self.model.objects.get(pk=pk)
        if not isinstance(obj, self.model):
            raise ValueError('Instance must be a {} object'.format(self.model))
        return obj

    def index(self, instance=None, pk=None, request=None):
        obj = self.get_object(instance, pk)
        doc = self.data_from_object(obj, request)
        self.es.index(self.index_name, self.type_label,
                      doc, obj.pk, refresh=True)

    def update(self, instance=None, pk=None, request=None):
        obj = self.get_object(instance, pk)
        doc = self.data_from_object(obj, request)
        self.es.update(self.index_name, self.type_label, obj.pk,
                       doc=doc, refresh=True)

    def remove(self, instance=None, pk=None):
        obj = self.get_object(instance, pk)
        self.es.delete(self.index_name, self.type_label, obj.pk)

    def update_all(self, qs=None, chunk_size=300):
        i = 0
        _qs = qs or self.model.objects.all()
        self.clear()
        self.put_mapping()

        # Break up qs into chunks & bulk index each
        while True:
            chunk = _qs[i:i + chunk_size]
            if not chunk:
                break
            data = [self.data_from_object(obj) for obj in chunk]
            self.es.bulk_index(self.index_name, self.type_label, data)
            i += chunk_size
