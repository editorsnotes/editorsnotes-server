from django.shortcuts import get_object_or_404

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from editorsnotes.main.models import Project, User
from editorsnotes.search import activity_index

__all__ = ['ActivityView']

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
        data = activity_index.get_activity_for(obj)
        return Response({ 'activity': data })


