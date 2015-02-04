from editorsnotes.main.models import Note

from .base import (BaseListAPIView, BaseDetailView, DeleteConfirmAPIView,
                   ElasticSearchListMixin)
from ..serializers.notes import NoteSerializer

__all__ = ['NoteList', 'NoteDetail', 'NoteConfirmDelete']


class NoteList(ElasticSearchListMixin, BaseListAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class NoteDetail(BaseDetailView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permissions = {
        'GET': ('main.view_private_note',),
        'HEAD': ('main.view_private_note',),
    }


class NoteConfirmDelete(DeleteConfirmAPIView):
    queryset = Note.objects.all()
    permissions = {
        'GET': ('main.delete_note',),
        'HEAD': ('main.delete_note',)
    }
