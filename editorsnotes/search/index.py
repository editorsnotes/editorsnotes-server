from lxml import etree
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from django.conf import settings

from editorsnotes.api import serializers
from editorsnotes.main import models

INDEX_NAME = 'editorsnotes'

es = ElasticSearch(settings.ELASTICSEARCH_URLS)

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

    def format_data(self, obj):
        data = { 
            'id': obj.id,
            'serialized': self.serializer(obj).data,
            'autocomplete': {
                'input': obj.as_text()
            }
        }
        return data

    def update(self, pk, data=None):
        if data is None:
            obj = self.model.objects.get(pk=pk)
            data = self.format_data(obj)
        es.index(INDEX_NAME, self.document_type, data)

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
            self.create_index()

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
