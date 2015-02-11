from rest_framework.permissions import SAFE_METHODS

from editorsnotes.main.models import Note

from .base import (BaseListAPIView, BaseDetailView, DeleteConfirmAPIView,
                   ElasticSearchListMixin)
from ..permissions import ProjectSpecificPermissions
from ..serializers.notes import NoteSerializer

__all__ = ['NoteList', 'NoteDetail', 'NoteConfirmDelete']

class NotePermissions(ProjectSpecificPermissions):
    authenticated_users_only = False
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super(NotePermissions, self).has_permission(request, view)
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS and obj.is_private:
            if request.user and request.user.is_authenticated():
                return request.user.has_project_perms(request.project,
                                                      'main.view_private_note')
        else:
            return True

        return False



class NoteList(ElasticSearchListMixin, BaseListAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

class NoteDetail(BaseDetailView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (NotePermissions,)


class NoteConfirmDelete(DeleteConfirmAPIView):
    queryset = Note.objects.all()
    permissions = {
        'GET': ('main.delete_note',),
        'HEAD': ('main.delete_note',)
    }
