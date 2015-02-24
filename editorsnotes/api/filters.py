from elasticsearch_dsl import Search, Q
from rest_framework.filters import BaseFilterBackend

from editorsnotes.search import get_index
from editorsnotes.search.utils import clean_query_string

BASE_QUERY = {'query': {'filtered': {'query': {'match_all': {}}}}}

class ElasticSearchFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query = Search()

        params = request.QUERY_PARAMS

        start = view.page_start
        count = view.page_count

        if hasattr(request, 'project') or 'project' in params:
            project_name = request.project.name \
                    if hasattr(request, 'project') \
                    else params['project']
            query = query.filter('term', **{ 'serialized.project.name': project_name })

        if 'updater' in params:
            filters.append({ 'term': { 'serialized.updater.username':
                                       params.get('updater') }})

        if 'q' in params:
            query = query.query('match', display_title={
                'query': params.get('q'),
                'operator': 'and',
                'fuzziness': '0.3'
            })
            query = query.highlight('_all').highlight_options({
                'pre_tags': ['&lt;strong&gt;'],
                'post_tags': ['&lt;/strong&gt;']
            })

        query = query.sort('-last_updated')
        query = query[start:start+count]
        en_index = get_index('main')
        return en_index.search_model(view.queryset.model, query.to_dict())

class ElasticSearchAutocompleteFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query = BASE_QUERY.copy()
        filters = []
        params = request.QUERY_PARAMS

        if hasattr(request, 'project') or 'project' in params:
            project = params.get('project', request.project.slug)
            filters.append({'term': {'serialized.project.url':
                                     '/projects/{}/'.format(project)}})

        term = clean_query_string(params.get('autocomplete').lower()).split()

        query['query']['filtered']['query'] = {
            'bool': { 'must': [], 'should': [] }
        }

        must = query['query']['filtered']['query']['bool']['must']
        should = query['query']['filtered']['query']['bool']['should']

        if len(term) > 1:
            must.append({
                'match': {
                    'display_title': {
                        'query': ' '.join(term[:-1]),
                        'operator': 'and',
                        'fuzziness': '0.2'
                    }
                }
            })

        must.append({
            'prefix': {
                'display_title': {
                    'value': term[-1]
                }
            }
        })

        should.append({
            'match_phrase': {
                'display_title': params.get('autocomplete').lower()
            }
        })

        should.append({
            'match': {
                'display_title': {
                    'query': ' '.join(term),
                    'operator': 'and'
                }
            }
        })

        query['fields'] = ['display_title', 'display_url']

        if filters:
            query['query']['filtered']['filter'] = { 'and': filters }

        if params.get('highlight'):
            query['highlight'] = {
                'fields': {'display_title': {'number_of_fragments': 0}},
                'pre_tags': ['&lt;strong&gt;'],
                'post_tags': ['&lt;/strong&gt;']
            }

        if hasattr(view, 'queryset') and view.queryset is not None:
            return en_index.search_model(view.queryset.model, query)
        else:
            # Should boost notes most of all
            return en_index.search(query)

