from rest_framework.pagination import LimitOffsetPagination


class ESLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 25
    limit_query_param = 'count'
    offset_query_param = 'start'
    max_limit = 200

    def paginate_queryset(self, search_query, request, view=None):
        raise Exception('This pagination class is only meant to work with '
                        'elasticsearch_dsl searches')

    def paginate_search(self, search, request, view=None):
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        self.request = request

        search = search[self.offset:self.offset + self.limit]
        search_results = search.execute()

        self.count = search_results.hits.total
        return search_results.hits.hits
