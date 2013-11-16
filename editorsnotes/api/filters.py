from rest_framework.filters import BaseFilterBackend

from editorsnotes.search import en_index

class ElasticSearchFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query = {'query': { 'filtered': { 'query': { 'match_all': {} } } } }
        filters = []

        params = request.QUERY_PARAMS

        if hasattr(request, 'project') or 'project' in params:
            project = params.get('project', request.project.slug)
            filters.append({ 'term': { 'serialized.project.url':
                                       '/projects/{}/'.format(project) }})

        if 'updater' in params:
            filters.append({ 'term': { 'serialized.updater.username':
                                       params.get('updater') }})

        if 'q' in params:
            q = params.get('q')
            query['query']['filtered']['query'] = {
                'match': {
                    'display_title': {
                        'query': q,
                        'operator': 'and',
                        'fuzziness': '0.3'
                    }
                }
            }
            query['highlight'] = {
                'fields': {'_all': {}},
                'pre_tags': ['&lt;strong&gt;'],
                'post_tags': ['&lt;/strong&gt;']
            }

        if filters:
            query['query']['filtered']['filter'] = { 'and': filters }

        return en_index.search_model(view.model, query)
