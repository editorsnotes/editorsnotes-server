"""
Functions for the items index.
"""

from itertools import chain

from django.utils.functional import SimpleLazyObject

from elasticsearch_dsl import F

from .utils import clean_query_string


def _get_index():
    from .index import ENIndex
    return ENIndex()

index = SimpleLazyObject(_get_index)


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
    query_filter = F('term', **{'serialized._embedded': item_url})

    if 'topic' in item_url:
        query_filter = query_filter | (
            F('term', **{'serialized.related_topic.url': item_url}))

    query = index.make_search()\
        .filter(query_filter)\
        .fields(['display_url'])

    return [(result.display_url[0]) for result in query.execute().hits]


def perform_query(query, highlight=False, **kwargs):
    if isinstance(query, basestring):
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
            for doc_type in index.document_types.values()
        ])
        for field_name in highlight_fields:
            prepared_query['highlight']['fields'][field_name] = {}

    return index.es.search(prepared_query, index=index.name, **kwargs)


def search_model(model, query, **kwargs):
    doc_type = index.document_types.get(model)
    return index.es.search(query, index=index.name,
                           doc_type=doc_type.type_label, **kwargs)
