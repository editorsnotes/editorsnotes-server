import json
from urlparse import urlparse

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from pyelasticsearch.exceptions import ElasticHttpNotFoundError
from rest_framework.renderers import JSONRenderer

from editorsnotes.api import serializers

class DocumentTypeAdapter(object):
    def __init__(self, es, index_name, model=None, highlight_fields=None,
                 display_field=None):
        self.model = model or self.get_model()
        self.type_label = getattr(self, 'type_label', self.model._meta.module_name)
        self.serializer = self.get_serializer()

        self.display_field = getattr(self, 'display_field', display_field)
        if self.display_field is None:
            raise ValueError(u'Define a display field for this document type '
                             '( {} )'.format(self))

        self.highlight_fields = getattr(self, 'highlight_fields', highlight_fields)
        
        self.es = es
        self.index_name = index_name

        self.dummy_request = self.make_dummy_request()

    def __unicode__(self):
        return self.model._meta.module_name

    def get_model(self):
        try:
            model = getattr(self, 'model')
        except AttributeError:
            raise NotImplementedError('Either set the `model` attribute or '
                                      'override get_model() to return a model.')
        return model

    def get_serializer(self):
        default_serializer_name = '{}Serializer'.format(self.model._meta.object_name)
        try:
            serializer = getattr(serializers, default_serializer_name)
        except AttributeError:
            raise NotImplementedError('Override this method to define a serializer.')
        return serializer

    def get_mapping(self):
        mapping = {
            self.type_label : {
                'properties': {
                    'display_url': { 'type': 'string', 'index': 'not_analyzed' },
                    'display_title': {
                        'search_analyzer': 'analyzer_shingle',
                        'index_analyzer': 'analyzer_shingle',
                        'type': 'string'
                    },
                    'serialized': {
                        'properties': {
                            'project': {
                                'properties': {
                                    'name': {'type': 'string', 'index': 'not_analyzed'},
                                    'url': {'type': 'string', 'index': 'not_analyzed' }
                                }
                            },
                            'related_topics': {
                                'properties': {
                                    'preferred_name': {'type': 'string', 'index': 'not_analyzed'},
                                    'url': {'type': 'string', 'index': 'not_analyzed'}
                                }
                            },
                        }
                    }
                }
            }
        }
        return mapping

    def clear(self):
        try:
            self.es.delete_all(self.index_name, self.type_label)
        except ElasticHttpNotFoundError:
            pass

    def put_mapping(self):
        mapping = self.get_mapping()
        self.es.put_mapping(self.index_name, self.type_label, mapping)

    def data_from_object(self, obj, request=None):
        if not hasattr(obj, '_rest_serialized'):
            context = { 'request': request or self.dummy_request }
            serializer = self.serializer(obj, context=context)
            data = json.loads(JSONRenderer().render(serializer.data))
            obj._rest_serialized = data
        data = {
            'id': obj.id,
            'serialized': obj._rest_serialized,
            'display_url': self.dummy_request.build_absolute_uri(obj.get_absolute_url()),
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

    def make_dummy_request(self):
        es_items_url = settings.ELASTICSEARCH_SITE
        parsed = urlparse(es_items_url)

        secure = parsed.scheme is 'https'
        hostname = parsed.hostname
        port = parsed.port or (443 if secure else 80)

        request = WSGIRequest({
            'REQUEST_METHOD': 'GET',
            'wsgi.input': '',
            'SERVER_NAME': hostname,
            'SERVER_PORT': port
        })
        if secure:
            request._is_secure = lambda: True
        return request

    def index(self, instance=None, pk=None, request=None):
        obj = self.get_object(instance, pk)
        doc = self.data_from_object(obj, request)
        self.es.index(self.index_name, self.type_label, doc, obj.pk, refresh=True)

    def update(self, instance=None, pk=None, request=None):
        obj = self.get_object(instance, pk)
        doc = self.data_from_object(obj, request)
        self.es.update(self.index_name, self.type_label, obj.pk, doc=doc, refresh=True)

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
            data = [ self.data_from_object(obj) for obj in chunk ]
            self.es.bulk_index(self.index_name, self.type_label, data)
            i += chunk_size
