from django.conf import settings

from elasticsearch_dsl import Q
from rest_framework.filters import BaseFilterBackend

from editorsnotes.search.utils import clean_query_string, make_dummy_request


class ProjectFilterBackend(object):
    "Filter the search's project base on either request or params"
    def filter_search(self, request, search, view):
        params = request.query_params

        if not (hasattr(request, 'project') or 'project' in params):
            return search

        request_project = getattr(request, 'project', None)

        # If in debug mode, always use a request based off of the base URL that
        # ES uses to index things, since it might be different from the passed
        # request URL. In production, requests should always be proxied and get
        # the same host.
        if settings.DEBUG:
            request = make_dummy_request()

        project_url = (
            request.build_absolute_uri(request_project.get_absolute_url())
            if request_project
            else params['project']
        )

        return search.filter('term', **{'serialized.project': project_url})


class UpdaterFilterBackend(object):
    """
    Filter searches based on updater in params

    FIXME: work with multiple updaters? -> this'll likely be part of a more
    general faceting strategy.
    """
    def filter_search(self, request, search, view):
        params = request.query_params
        if 'updater' not in params:
            return search

        return search.filter('term', **{
            'serialized.updater': params['updater']
        })


class QFilterBackend(object):
    "General filter based on the `q` parameter."
    def filter_search(self, request, search, view):
        q = request.query_params.get('q', None)
        if not q:
            return search

        # search = search.highlight('_all').highlight_options(**{
        #     'pre_tags': ['&lt;strong&gt;'],
        #     'post_tags': ['&lt;/strong&gt;']
        # })

        return search.query('match', display_title={
            'query': clean_query_string(q),
            'operator': 'and',
            'fuzziness': '0.3'
        })


# TODO: Make a new autocomplete filter.


ACTIVITY_TYPES = ['note', 'topic', 'document']
ACTIvITY_ACTIONS = ['added', 'changed', 'deleted']


class ActivityFilterBackend(BaseFilterBackend):
    def filter_search(self, request, search, view):
        params = request.query_params
        must = []

        if 'type' in params and params['type'] in ACTIVITY_TYPES:
            must.append(Q('term', **{'data.type': params['type']}))

        if 'action' in params and params['action'] in ACTIvITY_ACTIONS:
            must.append(Q('term', **{'data.action': params['action']}))

        if must:
            search.query = Q('bool', must=must)

        return search
