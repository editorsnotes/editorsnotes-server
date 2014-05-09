from collections import OrderedDict

from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
import reversion

from editorsnotes.main.models import Project
from editorsnotes.main.models.auth import RevisionProject
from editorsnotes.search import en_index

from ..filters import (ElasticSearchFilterBackend,
                       ElasticSearchAutocompleteFilterBackend)
from ..permissions import ProjectSpecificPermissions


def create_revision_on_methods(*methods):
    def make_revision_wrapper(fn):
        def wrapped(self, request, *args, **kwargs):
            with reversion.create_revision():
                ret = fn(self, request, *args, **kwargs)
                reversion.set_user(request.user)
                reversion.add_meta(RevisionProject, project=request.project)
            return ret
        return wrapped
    def klass_wrapper(klass):
        for method_name in methods:
            old_method = getattr(klass, method_name)
            wrapped = make_revision_wrapper(old_method)
            setattr(klass, method_name, wrapped)
        return klass
    return klass_wrapper

class ElasticSearchRetrieveMixin(RetrieveModelMixin):
    def retrieve(self, request, *args, **kwargs):

        if not settings.ELASTICSEARCH_ENABLED:
            return super(ElasticSearchRetrieveMixin, self).retrieve(request, *args, **kwargs)

        # Still need to get the object to check for perms
        self.object = self.get_object()
        data = en_index.data_for_object(self.object)
        return Response(data['_source']['serialized'])

class ElasticSearchListMixin(ListModelMixin):
    def list(self, request, *args, **kwargs):

        if not settings.ELASTICSEARCH_ENABLED:
            return super(ElasticSearchListMixin, self).list(request, *args, **kwargs)

        if 'autocomplete' in request.QUERY_PARAMS:
            self.filter_backend = ElasticSearchAutocompleteFilterBackend
            result = self.filter_queryset(None)
            data = {
                'count': result['hits']['total'],
                'results': []
            }
            for doc in result['hits']['hits']:
                r = OrderedDict()
                r['type'] = doc['_type']
                r['title'] = (
                    doc['highlight']['display_title'][0]
                    if 'highlight' in doc else
                    doc['fields']['display_title'])
                r['url'] = doc['fields']['serialized.url']
                data['results'].append(r)
        else:
            self.filter_backend = ElasticSearchFilterBackend
            result = self.filter_queryset(None)
            data = {
                'count': result['hits']['total'],
                'next': None,
                'previous': None,
                'results': [ doc['_source']['serialized'] for doc in
                             result['hits']['hits'] ]
            }
        return Response(data)


class ProjectSpecificMixin(object):
    def initialize_request(self, request, *args, **kwargs):
        request = super(ProjectSpecificMixin, self)\
                .initialize_request(request, *args, **kwargs)
        request._request.project = Project.objects.get(
            slug=kwargs.pop('project_slug'))
        return request
    def get_serializer_context(self):
        context = super(ProjectSpecificMixin, self).get_serializer_context()
        context['project'] = self.request.project
        return context
    def get_queryset(self):
        qs = super(ProjectSpecificMixin, self).get_queryset()
        if hasattr(qs.model, 'project'):
            qs = qs.filter(project_id=self.request.project.id)
        return qs

@create_revision_on_methods('create')
class BaseListAPIView(ProjectSpecificMixin, ListCreateAPIView):
    paginate_by = 50
    paginate_by_param = 'page_size'
    permission_classes = (ProjectSpecificPermissions,)
    parser_classes = (JSONParser,)
    def pre_save(self, obj):
        obj.creator = self.request.user
        if hasattr(obj.__class__, 'last_updater'):
            obj.last_updater = self.request.user
        super(BaseListAPIView, self).pre_save(obj)

@create_revision_on_methods('update', 'destroy')
class BaseDetailView(ProjectSpecificMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (ProjectSpecificPermissions,)
    parser_classes = (JSONParser,)
    def pre_save(self, obj):
        if hasattr(obj.__class__, 'last_updater'):
            obj.last_updater = self.request.user
        super(BaseDetailView, self).pre_save(obj)

@api_view(('GET',))
def root(request):
    return Response({
        'auth-token': reverse('api:obtain-auth-token', request=request),
        'topics': reverse('api:api-topic-nodes-list', request=request),
        'projects': reverse('api:api-projects-list', request=request),
        'search': reverse('api:api-search', request=request) + '?q={query},'
        #'notes': reverse('api:api-notes-list'),
        #'documents': reverse('api:api-documents-list')
    })
