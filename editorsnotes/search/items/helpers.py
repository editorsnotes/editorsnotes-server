"""
Functions for the items index.
"""

from collections import OrderedDict
from itertools import chain
from urllib.parse import urlparse

from elasticsearch_dsl import F

from django.core.urlresolvers import resolve

from . import index
from ..utils import clean_query_string, make_dummy_request


def data_for_object(obj):
    doc_type = index.document_types.get(obj.__class__, None)
    if doc_type is None:
        return None

    # will raise an exception if it's not there! should change
    return index.es.get(
        index=index.name, doc_type=doc_type.type_label, id=obj.id)


def get_referencing_items(item_url):
    """
    Get all items which have referenced the given item URL
    """

    if item_url.startswith('/'):
        item_url = make_dummy_request().build_absolute_uri(item_url)

    query_filter = F('term', **{'serialized.references': item_url})

    if 'topic' in item_url:
        query_filter = query_filter | (
            F('term', **{'serialized.related_topic.url': item_url}))

    query = index.make_search()\
        .filter(query_filter)\
        .fields(['url'])

    return [(result.url[0]) for result in query.execute().hits]


def get_data_for_urls(item_urls):
    docs = []
    ret = OrderedDict()

    if not item_urls:
        return ret

    item_urls = list(item_urls)
    item_urls.sort()

    request = make_dummy_request()

    for url in item_urls:
        path = urlparse(url).path
        match = resolve(path)
        model = match.func.cls.queryset.model

        doc_type = model._meta.verbose_name
        docs.append({
            '_type': doc_type,
            '_id': request.build_absolute_uri(path)
        })

    resp = index.es.multi_get(docs, index=index.name)

    for i, item_url in enumerate(item_urls):
        doc = resp['docs'][i]
        ret[item_url] = doc['_source']['serialized'] if doc['found'] else None

    return ret


def perform_query(query, highlight=False, **kwargs):
    if isinstance(query, str):
        prepared_query = {
            'query': {
                'query_string': {'query': clean_query_string(query)}
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
        highlight_fields = chain(*[
            doc_type.highlight_fields
            for doc_type in list(index.document_types.values())
        ])
        for field_name in highlight_fields:
            prepared_query['highlight']['fields'][field_name] = {}

    return index.es.search(prepared_query, index=index.name, **kwargs)


def search_model(model, query, **kwargs):
    doc_type = index.document_types.get(model)
    return index.es.search(query, index=index.name,
                           doc_type=doc_type.type_label, **kwargs)
