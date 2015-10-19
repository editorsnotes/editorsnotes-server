from collections import OrderedDict

from elasticsearch_dsl import Search
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from editorsnotes.api.serializers import ProjectSerializer
from editorsnotes.main.models import Note, Topic, Document
from editorsnotes.search import items as items_search

from ..hydra import project_links_for_request_user


__all__ = ['root', 'browse_items']


@api_view(('GET',))
def root(request, format=None):
    data = OrderedDict()

    if request.user.is_authenticated():
        data['affiliated_projects'] = {}

        projects = request.user.get_affiliated_projects()
        all_project_links = []

        for project in projects:
            links = project_links_for_request_user(project, request)

            serializer = ProjectSerializer(
                instance=project, context={'request': request})
            serializer.data
            serializer._data['@context'] = {
                link['url'].split('#')[1]: {
                    '@id': link['url'],
                    '@type': '@id',
                }
                for link in links
            }

            url = request.build_absolute_uri(project.get_absolute_url())
            data['affiliated_projects'][url] = serializer.data

            all_project_links += links
        data['links'] = all_project_links

    data['projects'] = reverse('api:projects-list', request=request)
    data['search'] = reverse('api:search', request=request)

    return Response(data)


def search_model(Model, query):
    query = query.to_dict()
    query['fields'] = ['display_title', 'display_url']
    results = items_search.search_model(Model, query)
    return [
        {
            'title': result['fields']['display_title'][0],
            'url': result['fields']['display_url'][0]
        }
        for result in results['hits']['hits']
    ]


@api_view(['GET'])
def browse_items(request, format=None):
    es_query = Search().sort('-serialized.last_updated')[:10]
    ret = OrderedDict()

    ret['topics'] = search_model(Topic, es_query)
    ret['documents'] = search_model(Document, es_query)
    ret['notes'] = search_model(Note, es_query.filter(
        'term', **{'serialized.is_private': 'false'}
    ))

    return Response(ret)
