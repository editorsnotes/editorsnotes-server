from rest_framework.filters import BaseFilterBackend

from editorsnotes.search import en_index
from editorsnotes.search.utils import clean_query_string

BASE_QUERY = {'query': {'filtered': {'query': {'match_all': {}}}}}

class ElasticSearchFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query = BASE_QUERY.copy()
        filters = []

        params = request.QUERY_PARAMS

        if hasattr(request, 'project') or 'project' in params:
            project = params.get('project', request.project.name)
            filters.append({ 'term': { 'serialized.project.name': project }})

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

        query['fields'] = ['display_title', 'serialized.url']

        if filters:
            query['query']['filtered']['filter'] = { 'and': filters }

        if params.get('highlight'):
            query['highlight'] = {
                'fields': {'display_title': {'number_of_fragments': 0}},
                'pre_tags': ['&lt;strong&gt;'],
                'post_tags': ['&lt;/strong&gt;']
            }

        if hasattr(view, 'model') and view.model is not None:
            return en_index.search_model(view.model, query)
        else:
            # Should boost notes most of all
            return en_index.search(query)

