"""
Index definitions
"""

from collections import OrderedDict
import json

from django.conf import settings

from elasticsearch_dsl import Search, analysis
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import InvalidJsonResponseError

from .types import DocumentTypeAdapter


class OrderedResponseElasticSearch(ElasticSearch):
    def _decode_response(self, response):
        try:
            json_response = json.loads(response.content,
                                       object_pairs_hook=OrderedDict)
        except ValueError:
            raise InvalidJsonResponseError(response)
        return json_response

    def search(self, *args, **kwargs):
        try:
            return super(OrderedResponseElasticSearch, self)\
                .search(*args, **kwargs)
        except TypeError as e:
            if 'body' in kwargs:
                kwargs['query'] = kwargs.pop('body')
                return super(OrderedResponseElasticSearch, self)\
                    .search(*args, **kwargs)
            else:
                raise e

    def count(self, *args, **kwargs):
        try:
            return super(OrderedResponseElasticSearch, self)\
                .count(*args, **kwargs)
        except TypeError as e:
            if 'body' in kwargs:
                kwargs['query'] = kwargs.pop('body')
                return super(OrderedResponseElasticSearch, self)\
                    .count(*args, **kwargs)
            else:
                raise e


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

    def make_search(self):
        "Return an elasticsearch_dsl Search object for this index"
        return Search(using=self.es, index=self.name)

    def delete(self):
        return self.es.delete_index(self.name)


class ENIndex(ElasticSearchIndex):
    """
    Index for main items: Notes, Topics, and Documents.

    Extends the main index to enable registration of document types which
    associated doc_types to custom mappings and model/serializer classes
    """
    def __init__(self):
        self.document_types = {}
        super(ENIndex, self).__init__()

    def put_mapping(self):
        self.put_type_mappings()

    def get_name(self):
        return settings.ELASTICSEARCH_PREFIX + '-items'

    def get_settings(self):
        shingle_filter = analysis.token_filter(
            'filter_shingle',
            'shingle',
            max_shingle_size=5,
            min_shingle_size=2,
            output_unigrams=True)

        shingle_analyzer = analysis.analyzer(
            'analyzer_shingle',
            tokenizer='standard',
            filter=['standard', 'lowercase', shingle_filter])

        return {
            'settings': {
                'index': {
                    'analysis': shingle_analyzer.get_analysis_definition()
                }
            }
        }

    def put_type_mappings(self):
        existing_types = self.es.get_mapping()\
            .get(self.name, {})\
            .get('mappings', {})\
            .keys()

        unmapped_types = (
            document_type for document_type in self.document_types
            if document_type not in existing_types)

        # TODO: Warn/log when a field's type mapping changes
        for document_type in unmapped_types:
            self.document_types[document_type].put_mapping()

    def register(self, model, adapter=None, highlight_fields=None,
                 display_field=None):

        doc_type = DocumentTypeAdapter(
            self.es, self.name, model, highlight_fields, display_field)
        self.document_types[model] = doc_type

        self.put_type_mappings()

    def make_search_for_model(self, model):
        doc_type = self.document_types.get(model)
        return self.make_search().doc_type(doc_type.type_label)


class ActivityIndex(ElasticSearchIndex):
    def get_name(self):
        return settings.ELASTICSEARCH_PREFIX + '-activitylog'
