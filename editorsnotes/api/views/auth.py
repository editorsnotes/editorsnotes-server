from collections import OrderedDict

from django.shortcuts import get_object_or_404

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from editorsnotes.auth.models import Project, User, LogActivity
from editorsnotes.search import activity_index

from ..filters import ActivityFilterBackend
from ..serializers import ProjectSerializer, UserSerializer
from ..serializers.hydra import (ProjectHydraClassesSerializer,
                                 link_properties_for_project)

from .mixins import (ElasticSearchListMixin, EmbeddedMarkupReferencesMixin,
                     HydraAffordancesMixin)

__all__ = ['ActivityView', 'ProjectList', 'ProjectDetail',
           'ProjectAPIDocumentation', 'UserDetail', 'SelfUserDetail']


class ProjectList(ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectDetail(HydraAffordancesMixin, RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_object(self):
        qs = self.get_queryset()
        project = get_object_or_404(qs, slug=self.kwargs['project_slug'])
        self.request.project = project
        return project

    def finalize_response(self, request, response, *args, **kwargs):
        project = self.get_object()

        response = super(ProjectDetail, self)\
            .finalize_response(request, response, *args, **kwargs)

        links = link_properties_for_project(project, request)
        context = {
            # FIXME: OrderedDict
            link['label']: {
                '@id': link['@id'],
                '@type': '@id',
            }
            for link in links
        }

        embedded = response.data.get('embedded', OrderedDict())
        for link in links:
            embedded[link['@id']] = link

        response.data['@context'] = context
        response.data['embedded'] = embedded

        return response


class ProjectAPIDocumentation(RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectHydraClassesSerializer

    def get_object(self):
        qs = self.get_queryset()
        project = get_object_or_404(qs, slug=self.kwargs['project_slug'])
        return project


class UserDetail(EmbeddedMarkupReferencesMixin, RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'


class SelfUserDetail(EmbeddedMarkupReferencesMixin, RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


def parse_int(val, default=25, maximum=100):
    if not isinstance(val, int):
        try:
            val = int(val)
        except ValueError:
            val = default
    return val if val <= maximum else maximum


class ActivityView(ElasticSearchListMixin, ListAPIView):
    """
    Recent activity for a user or project.

    Takes the following arguments:
        * type ("note", "topic", "document")
        * action ("add", "change", "delete")
    """

    es_filter_backends = (ActivityFilterBackend,)
    queryset = LogActivity.objects.all()

    def get_object(self):
        username = self.kwargs.get('username', None)
        project_slug = self.kwargs.get('project_slug', None)

        if username is not None:
            obj = get_object_or_404(User, username=username)
        elif project_slug is not None:
            obj = get_object_or_404(Project, slug=project_slug)
        else:
            raise ValueError()
        return obj

    def process_es_result(self, result):
        return result['_source']['data']

    def get_es_search(self):
        search = activity_index.make_search().sort('-time')
        obj = self.get_object()

        # FIXME FIXME FIXME: Users' and projects' actions should be indexed by
        # their URLs, not their usernames/slugs
        if isinstance(obj, User):
            search = search.filter('term', **{'data.user': obj.username})
        else:
            search = search.filter('term', **{'data.project': obj.slug})

        return search
