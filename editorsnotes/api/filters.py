from elasticsearch_dsl import Search, Q
from rest_framework.filters import BaseFilterBackend

from editorsnotes.search.utils import clean_query_string

BASE_QUERY = {'query': {'filtered': {'query': {'match_all': {}}}}}

# Filters should expect that the `queryset` parameter will be an instance of an
# elasticsearch_dsl.Search class. They should return another instance of that
# class which has any relevant changes applied.

class ElasticSearchFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = request.query_params
        search = queryset

        if hasattr(request, 'project') or 'project' in params:
            project_name = request.project.name \
                    if hasattr(request, 'project') \
                    else params['project']
            search = search.filter('term', **{ 'serialized.project.name': project_name })

        if 'updater' in params:
            search = search.filter('term', **{ 'serialized.updater.usernmae': params.get('updater') })

        if 'q' in params:
            search = search.query('match', display_title={
                'query': params.get('q'),
                'operator': 'and',
                'fuzziness': '0.3'
            })

            search = search.highlight('_all').highlight_options(**{
                'pre_tags': ['&lt;strong&gt;'],
                'post_tags': ['&lt;/strong&gt;']
            })

        search = search.sort('-last_updated')
        return search

class ElasticSearchAutocompleteFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query = BASE_QUERY.copy()
        filters = []
        params = request.query_params

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

