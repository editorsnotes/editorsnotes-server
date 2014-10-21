from django.shortcuts import get_object_or_404

from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from editorsnotes.main.models import Project, User
from editorsnotes.search import get_index

from ..serializers.projects import ProjectSerializer

__all__ = ['ActivityView', 'ProjectList', 'ProjectDetail']

class ProjectList(ListAPIView):
    model = Project
    serializer_class = ProjectSerializer

class ProjectDetail(RetrieveAPIView):
    model = Project
    serializer_class = ProjectSerializer
    def get_object(self):
        qs = self.get_queryset()
        project = get_object_or_404(qs, slug=self.kwargs['project_slug'])
        return project

class ActivityView(GenericAPIView):
    """
    Recent activity for a user or project.

    Takes the following arguments:

    * number (int)
    * start (int)
    * type ("note", "topic", "document", "transcript", "footnote")
    * action ("add", "change", "delete")
    * order ('asc' or 'desc')
    """
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
        data = get_index('activity').get_activity_for(obj)
        return Response({ 'activity': data })


