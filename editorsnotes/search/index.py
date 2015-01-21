from collections import OrderedDict
from itertools import chain
import json

from django.conf import settings

from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import InvalidJsonResponseError
from rest_framework.renderers import JSONRenderer

from editorsnotes.api.serializers import ActivitySerializer
from editorsnotes.main.models import Project, User

from .types import DocumentTypeAdapter
from .utils import clean_query_string

class OrderedResponseElasticSearch(ElasticSearch):
    def _decode_response(self, response):
        try:
            json_response = json.loads(response.content,
                                       object_pairs_hook=OrderedDict)
        except ValueError:
            raise InvalidJsonResponseError(response)
        return json_response

class ElasticSearchIndex(object):
    def __init__(self):
        if not hasattr(self, 'get_name'):
            raise NotImplementedError('Must implement get_name method')
        self.name = self.get_name()
        self.es = OrderedResponseElasticSearch(settings.ELASTICSEARCH_URLS)
        if not self.exists():
            self.create()
            self.created = True
        else:
            self.created = False

    def get_settings(self):
        return {}

    def put_mapping(self):
        "Override to put mappings for inherited indices."
        pass

    def exists(self):
        server_url, _ = self.es.servers.get()
        resp = self.es.session.head(server_url + '/' + self.name)
        return resp.status_code == 200

    def create(self):
        created = self.es.create_index(self.name, self.get_settings())
        self.put_mapping()
        return created

    def delete(self):
        return self.es.delete_index(self.name)


class ENIndex(ElasticSearchIndex):
    def __init__(self):
        self.document_types = {}
        super(ENIndex, self).__init__()

    def put_mapping(self):
        self.put_type_mappings()

    def get_name(self):
        return settings.ELASTICSEARCH_PREFIX + '-items'

    def get_settings(self):
        return {
            'settings': {
                'index': {
                    'analysis': {
                        'analyzer': {
                            'analyzer_shingle': {
                                'tokenizer': 'standard',
                                'filter': ['standard', 'lowercase', 'filter_shingle']
                            }
                        },
                        'filter': {
                            'filter_shingle': {
                                'type': 'shingle',
                                'max_shingle_size': 5,
                                'min_shingle_size': 2,
                                'output_unigrams': True
                            }
                        }
                    }
                }
            }
        }

    def put_type_mappings(self):
        existing_types = self.es.get_mapping()\
                .get(self.name, {})\
                .get('mappings', {})\
                .keys()

        unmapped_types = (document_type for document_type in self.document_types
                          if document_type not in existing_types)

        # TODO: Warn/log when a field's type mapping changes
        for document_type in unmapped_types:
            self.document_types[document_type].put_mapping()

    def register(self, model, adapter=None, highlight_fields=None,
                 display_field=None):

        if adapter is None:
            doc_type = DocumentTypeAdapter(self.es, self.name, model,
                                           highlight_fields, display_field)
        else:
            doc_type = adapter(self.es, self.name, model)
        self.document_types[model] = doc_type

        self.put_type_mappings()

    def data_for_object(self, obj):
        doc_type = self.document_types.get(obj.__class__, None)
        if doc_type is None:
            return None

        # will raise an exception if it's not there! should change
        return self.es.get(index=self.name, doc_type=doc_type.type_label,
                           id=obj.id)

    def search_model(self, model, query, **kwargs):
        doc_type = self.document_types.get(model)
        return self.es.search(query, index=self.name,
                              doc_type=doc_type.type_label, **kwargs)

    def search(self, query, highlight=False, **kwargs):
        if isinstance(query, basestring):
            prepared_query = {
                'query': {
                    'query_string': { 'query': clean_query_string(query) }
                }
            }

        else:
            prepared_query = query

        if highlight:
            prepared_query['highlight'] = {
                'fields': {},
                'pre_tags': ['<span class="highlighted">'],
                'post_tags': ['</span>']
            }
            highlight_fields = chain(
                *[doc_type.highlight_fields
                for doc_type in self.document_types.values()])
            for field_name in highlight_fields:
                prepared_query['highlight']['fields'][field_name] = {}

        return self.es.search(prepared_query, index=self.name, **kwargs)

class ActivityIndex(ElasticSearchIndex):
    def get_name(self):
        return settings.ELASTICSEARCH_PREFIX + '-activitylog'
    def get_activity_for(self, entity, es_query=None, size=25):
        query = es_query or {}
        if not 'size' in query:
            query['size'] = size
        if not 'sort' in query:
            query['sort'] = {
                'data.time': { 'order': 'desc', 'ignore_unmapped': True }
            }
        if not 'query' in query:
            query['query'] = {'filtered': {'filter': {'bool': { 'must': []}}}}

        if isinstance(entity, User):
            query['query']['filtered']['filter']['bool']['must'].append({
                'term': { 'data.user': entity.username }
            })
        elif isinstance(entity, Project):
            query['query']['filtered']['filter']['bool']['must'].append({
                'term': { 'data.project': entity.slug }
            })
        else:
            raise ValueError('Must pass either project or user')

        search = self.es.search(query, index=self.name)
        return [ hit['_source']['data'] for hit in search['hits']['hits'] ]

    def handle_edit(self, instance, refresh=True):
        serializer = ActivitySerializer(instance)
        data = json.loads(JSONRenderer().render(serializer.data),
                          object_pairs_hook=OrderedDict)

        self.es.index(self.name, 'activity',
                      { 'id': instance.id, 'data': data },
                      refresh=refresh)
