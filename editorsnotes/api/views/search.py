from collections import OrderedDict

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from editorsnotes.search import items as items_search

from ..filters import ElasticSearchAutocompleteFilterBackend

__all__ = ['SearchView']


class SearchView(GenericAPIView):
    def get(self, request, format=None):
        query = {'query': {}}
        params = request.query_params

        if 'autocomplete' in params:
            self.filter_backend = ElasticSearchAutocompleteFilterBackend
            result = self.filter_queryset(None)
            data = {
                'count': result['hits']['total'],
                'results': [
                    OrderedDict((
                        ('type', doc['_type']),
                        ('title', doc['highlight' if 'highlight' in doc else
                                      'fields']['display_title'][0 if
                                                                 'highlight' in
                                                                 doc else 0:None]),
                        ('url', doc['fields']['display_url'])
                    )) for doc in result['hits']['hits']
                ]
            }
            return Response(data)

        if 'q' in params:
            query['query']['query_string'] = {'query': params.get('q')}

        if 'sort' in params:
            pass

        if 'order' in params:
            pass

        if 'page' in params:
            pass

        if not query['query']:
            query = {'query': {'match_all': {}}}

        es_query = items_search(query)

        hits = []

        for hit in es_query['hits']['hits']:
            item_type = hit['_type']
            item_data = hit['_source']['serialized']
            filter_method = getattr(self, 'filter_{}_hits'.format(item_type),
                                    None)
            if filter_method is not None:
                item_data = filter_method(item_data)
            hits.append({'data': item_data, 'type': item_type})

        return Response(OrderedDict((
            ('results', es_query['hits']['total']),
            ('data', hits),
        )))
