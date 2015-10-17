from rest_framework.generics import ListAPIView
from rest_framework.permissions import SAFE_METHODS

from editorsnotes.main.models import Note

from .base import (BaseListAPIView, BaseDetailView, DeleteConfirmAPIView,
                   ElasticSearchListMixin, LinkerMixin,
                   EmbeddedMarkupReferencesMixin)
from ..linkers import (AddProjectObjectLinker, EditProjectObjectLinker,
                       DeleteProjectObjectLinker)
from ..permissions import ProjectSpecificPermissions
from ..serializers.notes import NoteSerializer

__all__ = ['NoteList', 'NoteDetail', 'AllProjectNoteList',
           'NoteConfirmDelete']


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


class NoteList(ElasticSearchListMixin, LinkerMixin, BaseListAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    linker_classes = (AddProjectObjectLinker,)


class NoteDetail(EmbeddedMarkupReferencesMixin, BaseDetailView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (NotePermissions,)
    linker_classes = (EditProjectObjectLinker, DeleteProjectObjectLinker,)


class AllProjectNoteList(ElasticSearchListMixin, LinkerMixin, ListAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    # FIXME: Only show notes that aren't private


class NoteConfirmDelete(DeleteConfirmAPIView):
    queryset = Note.objects.all()
    permissions = {
        'GET': ('main.delete_note',),
        'HEAD': ('main.delete_note',)
    }
