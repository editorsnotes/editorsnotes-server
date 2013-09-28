from collections import OrderedDict
import json

from lxml import etree
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import (
    ElasticHttpNotFoundError, InvalidJsonResponseError)

from django.conf import settings

from editorsnotes.api import serializers
from editorsnotes.main import models

INDEX_NAME = settings.ELASTICSEARCH_INDEX_NAME

class OrderedResponseElasticSearch(ElasticSearch):
    def _decode_response(self, response):
        try:
            json_response = json.loads(response.content,
                                       object_pairs_hook=OrderedDict)
        except ValueError:
            raise InvalidJsonResponseError(response)
        return json_response

es = OrderedResponseElasticSearch(settings.ELASTICSEARCH_URLS)

class DocumentType(object):
    def __init__(self, model=None):
        self.model = model or self.get_model()
        self.serializer = self.get_serializer()
        self.document_type = self.model._meta.module_name

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
            self.document_type: {
                'properties': {
                    'autocomplete': {
                        'type': 'completion',
                        'payloads': True
                    }
                }
            }
        }
        return mapping

    def clear(self):
        try:
            es.delete_all(INDEX_NAME, self.document_type)
        except ElasticHttpNotFoundError:
            pass

    def data_from_serializer(self, obj):
        return self.serializer(obj).data

    def format_data(self, obj):
        if not hasattr(obj, '_rest_serialized'):
            obj._rest_serialized = self.serializer(obj).data
        data = { 
            'id': obj.id,
            'serialized': obj._rest_serialized,
            'autocomplete': { 'input': obj.as_text() }
        }
        return data

    def get_object(self, instance=None, pk=None):
        if pk is None and instance is None:
            raise ValueError('Provide either a pk or instance to update.')
        obj = instance or self.model.objects.get(pk=pk)
        if not isinstance(obj, self.model):
            raise ValueError('Instance must be a {} object'.format(self.model))
        return obj

    def index(self, instance=None, pk=None):
        obj = self.get_object(instance, pk)
        doc = self.format_data(obj)
        es.index(INDEX_NAME, self.document_type, doc, obj.pk, refresh=True)

    def update(self, instance=None, pk=None):
        obj = self.get_object(instance, pk)
        doc = self.format_data(obj)
        es.update(INDEX_NAME, self.document_type, obj.pk, doc=doc, refresh=True)

    def remove(self, instance=None, pk=None):
        obj = self.get_object(instance, pk)
        es.delete(INDEX_NAME, self.document_type, obj.pk)

    def update_all(self, chunk_size=300):
        i = 0
        qs = self.model.objects.all()
        self.clear()

        # Break up qs into chunks & bulk index each
        while True:
            chunk = qs[i:i + chunk_size]
            if not chunk:
                break
            data = [ self.format_data(obj) for obj in chunk ]
            es.bulk_index(INDEX_NAME, self.document_type, data)
            i += chunk_size

class ENIndex(object):
    def __init__(self, name=INDEX_NAME):
        self.document_types = {}
        self.name = name
        self.es = es
        if not self.exists():
            self.create()

    def exists(self):
        server_url, _ = self.es.servers.get()
        resp = self.es.session.head(server_url + '/' + self.name)
        return resp.status_code == 200

    def register(self, model):
        doc_type = DocumentType(model)
        self.document_types[model] = doc_type

    def data_for_object(self, obj):
        doc_type = self.document_types.get(obj.__class__, None)
        if doc_type is None:
            return None

        # will raise an exception if it's not there! should change
        return self.es.get(index=self.name, doc_type=doc_type.document_type,
                           id=obj.id)

    def search_model(self, model, query, **kwargs):
        doc_type = self.document_types.get(model)
        return self.es.search(query, index=self.name,
                              doc_type=doc_type.document_type, **kwargs)
        

    def create(self):
        created = self.es.create_index(self.name)
        for doc_type in self.document_types.values():
            self.es.put_mapping(doc_type.get_mapping())
        return created

    def delete(self):
        return self.es.delete_index(self.name)

en_index = ENIndex()
en_index.register(models.Document)
en_index.register(models.Note)
