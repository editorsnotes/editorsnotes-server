from collections import OrderedDict
import json

from django.conf import settings

from elasticsearch_dsl import Search
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import InvalidJsonResponseError


class OrderedResponseElasticSearch(ElasticSearch):
    """
    Extension of pyelasticsearch.ElasticSearch that decodes responses using an
    OrderedDict instead of a plain dict.
    """
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
    """
    Base index definition which should be inherited by other indices.
    """
    name = None

    mappings = None
    settings = None

    def __init__(self):
        if self.name is None:
            raise ValueError('ElasticSearchIndex subclasses must have a name')

        self.name = settings.ELASTICSEARCH_PREFIX + '-' + self.name
        self.es = OrderedResponseElasticSearch(settings.ELASTICSEARCH_URLS)

    def get_mappings(self):
        return self.mappings or {}

    def get_settings(self):
        return self.settings or {}

    def initialize(self):
        if not self.exists():
            self.create()
        self.put_all_mappings()

    def put_all_mappings(self):
        for doc_type, mapping in list(self.get_mappings().items()):
            self.es.put_mapping(self.name, doc_type, mapping)

    def exists(self):
        server_url, _ = self.es.servers.get()
        resp = self.es.session.head(server_url + '/' + self.name)
        return resp.status_code == 200

    def create(self):
        return self.es.create_index(self.name, self.get_settings())

    def delete(self):
        return self.es.delete_index(self.name)

    def make_search(self):
        "Return an elasticsearch_dsl Search object for this index"
        return Search(using=self.es, index=self.name)
