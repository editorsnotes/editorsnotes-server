from collections import OrderedDict
from itertools import chain
import json

from django.conf import settings

from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import InvalidJsonResponseError
from reversion.models import VERSION_ADD, VERSION_CHANGE, VERSION_DELETE

from editorsnotes.main.models import Project, User

from .types import DocumentTypeAdapter

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
        return created

    def delete(self):
        return self.es.delete_index(self.name)


class ENIndex(ElasticSearchIndex):
    def __init__(self):
        super(ENIndex, self).__init__()
        self.document_types = {}

    def put_mapping(self):
        for doc_type in self.document_types:
            self.document_types[doc_type].put_mapping()

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

    def register(self, model, adapter=None, highlight_fields=None,
                 display_field=None):

        if adapter is None:
            doc_type = DocumentTypeAdapter(self.es, self.name, model,
                                           highlight_fields, display_field)
        else:
            doc_type = adapter(self.es, self.name, model)
        self.document_types[model] = doc_type

        if not self.created:
            existing_types = self.es.get_mapping()[self.name]['mappings']['keys']
            put_type_mapping = doc_type.type_label not in existing_types
        else:
            put_type_mapping = True

        if put_type_mapping:
            doc_type.put_mapping()

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
                    'query_string': { 'query': query }
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

VERSION_ACTIONS = {
    VERSION_ADD: 'added',
    VERSION_CHANGE: 'changed',
    VERSION_DELETE: 'deleted'
}

class ActivityIndex(ElasticSearchIndex):
    def get_name(self):
        return settings.ELASTICSEARCH_PREFIX + '-activitylog'
    def get_activity_for(self, entity, size=25, **kwargs):
        query = {
            'query': {},
            'sort': {'data.time': { 'order': 'desc', 'ignore_unmapped': True }}
        }
        if isinstance(entity, User):
            query['query']['match'] = { 'data.user': entity.username }
        elif isinstance(entity, Project):
            query['query']['match'] = { 'data.project': entity.slug }
        else:
            raise ValueError('Must pass either project or user')
        query.update(kwargs)
        search = self.es.search(query, index=self.name, size=size)
        return [ hit['_source']['data'] for hit in search['hits']['hits'] ]

    def data_from_reversion_version(self, version):
        url = version.object and version.object.get_absolute_url()
        return {
            'data': OrderedDict((
                ('user', version.revision.user.username,),
                ('project', version.revision.project_metadata.project.slug,),
                ('time', version.revision.date_created,),
                ('type', version.content_type.model,),
                ('url', url),
                ('title', version.object_repr,),
                ('action', VERSION_ACTIONS[version.type],),
            )),
            'object_id': version.object_id_int,
            'version_id': version.id
        }

    def handle_edit(self, instance, version):
        self.es.index(self.name, 'activity',
                      self.data_from_reversion_version(version))
