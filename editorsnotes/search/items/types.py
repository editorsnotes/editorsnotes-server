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
        ['serialized.title', 'serialized.markup_html']
    ),
    (
        'Topic',
        ['serialized.preferred_name', 'serialized.markup_html']
    ),
    (
        'Document',
        ['serialized.description']
    ),
    (
        'Project',
        ['serialized.description']
    ),
    (
        'Transcript',
        ['serialized_markup_html']
    )
)


class DocumentTypeConfig(object):
    def __init__(self, es, index_name, model_name,
                 highlight_fields=None):

        from editorsnotes.api import serializers
        main = apps.get_app_config('main')
        auth = apps.get_app_config('auth')

        self.es = es
        self.index_name = index_name

        try:
            self.model = main.get_model(model_name)
        except LookupError:
            self.model = auth.get_model(model_name)

        self.doctype = getattr(mappings, '{}DocType'.format(model_name))
        self.serializer = getattr(
            serializers, '{}Serializer'.format(model_name))

        self.highlight_fields = highlight_fields or []

        self.request = make_dummy_request()

    @property
    def type_label(self):
        return self.doctype._doc_type.name

    @property
    def type_mapping(self):
        mapping = self.doctype._doc_type.mapping.to_dict()
        return mapping

    def make_type_kwargs(self, kwargs):
        kwargs.update({
            'index': self.index_name,
            'doc_type': self.type_label
        })
        return kwargs

    def clear(self):
        try:
            self.es.delete_all(self.index_name, self.type_label)
            self.es.put_mapping(self.index_name, self.type_label,
                                self.type_mapping)
        except ElasticHttpNotFoundError:
            pass

    def data_from_object(self, obj):
        serializer = self.serializer(obj, context={'request': self.request})
        json_data = JSONRenderer().render(serializer.data)
        serialized = json.loads(json_data.decode('utf-8'), object_pairs_hook=OrderedDict)

        # All items' ES IDs will be the URLs. However, their PKs from the
        # database will also be stored for convenience.
        url = serialized['url']
        data = {
            'pk': obj.pk,
            'url': url,
            'serialized': serialized,
            'display_title': obj.as_text()
        }

        return data

    def index(self, instance):
        doc = self.data_from_object(instance)
        self.es.index(**self.make_type_kwargs({
            'doc': doc,
            'id': doc['url'],
            'refresh': True
        }))

    def update(self, instance):
        doc = self.data_from_object(instance)
        self.es.update(**self.make_type_kwargs({
            'doc': doc,
            'id': doc['url'],
            'refresh': True
        }))

    def remove(self, instance):
        doc_id = self.request.build_absolute_uri(instance.get_absolute_url())
        self.es.delete(**self.make_type_kwargs({
            'id': doc_id,
            'refresh': True
        }))

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
            self.es.bulk_index(self.index_name, self.type_label, data,
                               id_field='url')
            i += chunk_size
