from django.shortcuts import get_object_or_404

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from editorsnotes.auth.models import Project, User
from editorsnotes.search import activity_index

from ..filters import ActivityFilterBackend
from ..linkers import ActivityLinker
from ..serializers import ProjectSerializer, UserSerializer

from .mixins import (ElasticSearchListMixin, EmbeddedMarkupReferencesMixin,
                     LinkerMixin)

__all__ = ['ActivityView', 'ProjectList', 'ProjectDetail', 'UserDetail',
           'SelfUserDetail']


class ProjectList(ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectDetail(LinkerMixin, RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    linker_classes = (ActivityLinker,)

    def get_object(self):
        qs = self.get_queryset()
        project = get_object_or_404(qs, slug=self.kwargs['project_slug'])
        return project


class UserDetail(EmbeddedMarkupReferencesMixin, LinkerMixin, RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    linker_classes = (ActivityLinker,)
    lookup_field = 'username'


class SelfUserDetail(EmbeddedMarkupReferencesMixin, LinkerMixin,
                     RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    linker_classes = (ActivityLinker,)

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
        search = activity_index.make_search()
        obj = self.get_object()

        # FIXME FIXME FIXME: Users' and projects' actions should be indexed by
        # their URLs, not their usernames/slugs
        if isinstance(obj, User):
            search = search.filter('term', **{'data.user': obj.username})
        else:
            search = search.filter('term', **{'data.project': obj.slug})

        return search
