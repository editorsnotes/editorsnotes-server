from rest_framework.generics import ListAPIView
from rest_framework.permissions import SAFE_METHODS

from editorsnotes.main.models import Note

from .. import filters as es_filters
from ..permissions import ProjectSpecificPermissions
from ..serializers.notes import NoteSerializer

from .base import BaseListAPIView, BaseDetailView, DeleteConfirmAPIView
from .mixins import (ElasticSearchListMixin, EmbeddedReferencesMixin,
                     HydraAffordancesMixin)

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


class NoteList(ElasticSearchListMixin, BaseListAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    es_filter_backends = (
        es_filters.ProjectFilterBackend,
        es_filters.QFilterBackend,
        es_filters.UpdaterFilterBackend,
    )


class NoteDetail(EmbeddedReferencesMixin, HydraAffordancesMixin,
                 BaseDetailView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (NotePermissions,)


class AllProjectNoteList(ElasticSearchListMixin, ListAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    # FIXME: Only show notes that aren't private


class NoteConfirmDelete(DeleteConfirmAPIView):
    queryset = Note.objects.all()
    permissions = {
        'GET': ('main.delete_note',),
        'HEAD': ('main.delete_note',)
    }
