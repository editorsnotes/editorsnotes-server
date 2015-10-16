from collections import OrderedDict
import json

from pyelasticsearch.exceptions import ElasticHttpNotFoundError
from rest_framework.renderers import JSONRenderer

from django.apps import apps

from ..utils import make_dummy_request
from . import mappings


DEFINED_TYPES = (
    (
        'Note',
        'id',
        'serialized.title',
        ['serialized.title', 'serialized.markup_html']
    ),
    (
        'Topic',
        'id',
        'serialized.preferred_name',
        ['serialized.preferred_name', 'serialized.markup_html']
    ),
    (
        'Document',
        'id',
        'serialized.description',
        ['serialized.description']
    ),
    (
        'Project',
        'slug',
        'serialized.descripton',
        ['serialized.description']
    )
)


class DocumentTypeConfig(object):
    def __init__(self, es, index_name, model_name, id_field, display_field,
                 highlight_fields=None):

        from editorsnotes.api import serializers
        main = apps.get_app_config('main')
        auth = apps.get_app_config('auth')

        self.es = es
        self.index_name = index_name
        self.id_field = id_field
        self.doc_id_field = 'serialized.{}'.format(self.id_field)

        try:
            self.model = main.get_model(model_name)
        except LookupError:
            self.model = auth.get_model(model_name)

        self.doctype = getattr(mappings, '{}DocType'.format(model_name))
        self.serializer = getattr(
            serializers, '{}Serializer'.format(model_name))

        self.highlight_fields = highlight_fields or []

    @property
    def type_label(self):
        return self.doctype._doc_type.name

    @property
    def type_mapping(self):
        mapping = self.doctype._doc_type.mapping.to_dict()
        return mapping

    def clear(self):
        try:
            self.es.delete_all(self.index_name, self.type_label)
            self.es.put_mapping(self.index_name, self.type_label,
                                self.type_mapping)
        except ElasticHttpNotFoundError:
            pass

    def data_from_object(self, obj, request=None):
        request = request or make_dummy_request()

        if not hasattr(obj, '_rest_serialized'):
            serializer = self.serializer(obj, context={'request': request})
            json_data = json.loads(JSONRenderer().render(serializer.data),
                                   object_pairs_hook=OrderedDict)
            obj._rest_serialized = json_data
        else:
            json_data = obj._rest_serialized.copy()
            json_data.pop('_embedded', None)

        data = {
            'id': getattr(obj, self.id_field),
            'serialized': json_data,
            'display_url': request.build_absolute_uri(obj.get_absolute_url()),
            'display_title': obj.as_text()
        }

        return data

    def get_object(self, instance=None, id_lookup=None):
        if id_lookup is None and instance is None:
            raise ValueError('Provide either an instance or a lookup value '
                             'to retrieve a given {}'.format(self.type_label))

        if instance and not isinstance(instance, self.model):
            raise ValueError('Instance must be a {} object'.format(self.model))

        obj = instance or self.model.objects.get({self.id_field: id_lookup})

        return obj

    def index(self, instance=None, id_lookup=None, request=None):
        obj = self.get_object(instance, id_lookup)
        doc = self.data_from_object(obj, request)
        doc_id = getattr(obj, self.id_field)

        self.es.index(self.index_name, self.type_label, doc, doc_id,
                      refresh=True)

    def update(self, instance=None, id_lookup=None, request=None):
        obj = self.get_object(instance, id_lookup)
        doc = self.data_from_object(obj, request)
        doc_id = getattr(obj, self.id_field)
        self.es.update(self.index_name, self.type_label, doc_id, doc=doc,
                       refresh=True)

    def remove(self, instance=None, id_lookup=None):
        obj = self.get_object(instance, id_lookup)
        doc_id = getattr(obj, self.id_field)
        self.es.delete(self.index_name, self.type_label, doc_id, refresh=True)

    def update_all(self, qs=None, chunk_size=300):
        i = 0
        _qs = qs or self.model.objects.all()
        self.clear()

        # Break up qs into chunks & bulk index each
        while True:
            chunk = _qs[i:i + chunk_size]
            if not chunk:
                break
            data = [self.data_from_object(obj) for obj in chunk]
            self.es.bulk_index(self.index_name, self.type_label, data)
            i += chunk_size
