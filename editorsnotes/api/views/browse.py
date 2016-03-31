from collections import OrderedDict

from elasticsearch_dsl import Search
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from editorsnotes.api.serializers import ProjectSerializer
from editorsnotes.api.serializers.hydra import link_properties_for_project
from editorsnotes.auth.models import Project
from editorsnotes.main.models import Note, Topic, Document
from editorsnotes.search import items_index


__all__ = ['root', 'browse_items']


@api_view(('GET',))
def root(request, format=None):
    data = OrderedDict()

    data['projects'] = reverse('api:projects-list', request=request)
    data['search'] = reverse('api:search', request=request)

    if request.user.is_authenticated():
        data['embedded'] = OrderedDict()

        projects = request.user.get_affiliated_projects()

        for project in projects:
            project_serializer = ProjectSerializer(project, context={
                'request': request
            })

            url = request.build_absolute_uri(project.get_absolute_url())

            project_data = OrderedDict()
            project_data['@context'] = {
                'notes': {
                    "@type": "@id",
                    "@id": url + 'vocab#Project/notes'
                },
                'topics': {
                    "@type": "@id",
                    "@id": url + 'vocab#Project/topics'
                },
                'documents': {
                    "@type": "@id",
                    "@id": url + 'vocab#Project/documents'
                },
            }

            project_data.update(project_serializer.data)

            data['embedded'][url] = project_data
            link_properties = link_properties_for_project(project, request)

            for link in link_properties:
                data['embedded'][link['@id']] = link

    return Response(data)


def search_model(Model, query):
    es_query = items_index\
        .make_search_for_model(Model)\
        .fields(['display_title', 'url'])

    results = es_query.execute()

    return [
        { 'title': result.display_title[0], 'url': result.url[0] }
        for result in results.hits
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
    ret['projects'] = search_model(Project, es_query)

    return Response(ret)
