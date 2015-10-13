from django.shortcuts import get_object_or_404

from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from editorsnotes.auth.models import Project, User
from editorsnotes.search import activity as activity_search

from .base import LinkerMixin
from ..linkers import ActivityLinker
from ..serializers import ProjectSerializer, MinimalUserSerializer, UserSerializer

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

class UserDetail(LinkerMixin, RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = MinimalUserSerializer
    linker_classes = (ActivityLinker,)
    lookup_field = 'username'

class SelfUserDetail(LinkerMixin, RetrieveAPIView):
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

class ActivityView(GenericAPIView):
    """
    Recent activity for a user or project.

    Takes the following arguments:

    * count (int)
    * start (int)
    * type ("note", "topic", "document", "transcript", "footnote")
    * action ("add", "change", "delete")
    * order ('asc' or 'desc')
    """
    TYPES = ['note', 'topic', 'document', 'transcript', 'footnote']
    ACTIONS = ['added', 'changed', 'deleted']
    def get_es_query(self):
        q = {'query': {'filtered': {'filter': {'bool': { 'must': []}}}}}
        params = self.request.query_params
        if 'count' in params:
            q['size'] = parse_int(params['count'])
        if 'start' in params:
            q['from'] = parse_int(params['start'])
        if 'type' in params and params['type'] in self.TYPES:
            q['query']['filtered']['filter']['bool']['must'].append({
                'term': { 'data.type': params['type'] }
            })
        if 'action' in params and params['action'] in self.ACTIONS:
            q['query']['filtered']['filter']['bool']['must'].append({
                'term': { 'data.action': params['action'] }
            })
        return q
    def get_object(self, username=None, project_slug=None):
        if username is not None:
            obj = get_object_or_404(User, username=username)
        elif project_slug is not None:
            obj = get_object_or_404(Project, slug=project_slug)
        else:
            raise ValueError()
        return obj
    def get(self, request, format=None, **kwargs):
        obj = self.get_object(**kwargs)
        es_query = self.get_es_query()

        data = activity_search.get_activity_for(obj, es_query)
        return Response({ 'activity': data })
