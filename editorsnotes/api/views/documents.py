from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser

from editorsnotes.main.models import Document, Scan, Transcript

from ..linkers import (AddProjectObjectLinker, EditProjectObjectLinker,
                       DeleteProjectObjectLinker)
from ..serializers import (DocumentSerializer, ScanSerializer,
                           TranscriptSerializer)

from .base import BaseListAPIView, BaseDetailView, DeleteConfirmAPIView
from .mixins import ElasticSearchListMixin, LinkerMixin

__all__ = ['DocumentList', 'DocumentDetail', 'DocumentConfirmDelete',
           'ScanList', 'ScanDetail', 'Transcript']


class DocumentList(ElasticSearchListMixin, LinkerMixin, BaseListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    linker_classes = (AddProjectObjectLinker,)


class DocumentDetail(BaseDetailView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    linker_classes = (EditProjectObjectLinker, DeleteProjectObjectLinker,)


class DocumentConfirmDelete(DeleteConfirmAPIView):
    queryset = Document.objects.all()
    permissions = {
        'GET': ('main.delete_document',),
        'HEAD': ('main.delete_document',)
    }


class ScanList(BaseListAPIView):
    model = Scan
    serializer_class = ScanSerializer
    parser_classes = (MultiPartParser,)
    paginate_by = None

    def get_serializer(self, *args, **kwargs):
        # Allow multiple images to be uploaded at once
        kwargs['data'] = [
            {'image': image} for image in kwargs['data'].getlist('image')
        ]
        kwargs['many'] = True
        return super(ScanList, self).get_serializer(*args, **kwargs)

    def get_document(self):
        document_id = self.kwargs.get('document_id')
        document_qs = Document.objects.prefetch_related('scans__creator')
        document = get_object_or_404(document_qs, id=document_id)
        return document

    def get_queryset(self):
        return self.get_document().scans.all()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,
                        document_id=self.kwargs.get('document_id'))


class ScanDetail(BaseDetailView):
    model = Scan
    serializer_class = ScanSerializer
    parser_classes = (MultiPartParser,)

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        document_id = self.kwargs.get('document_id')
        scan_id = self.kwargs.get('scan_id')
        document_qs = Document.objects.prefetch_related('scans__creator')
        document = get_object_or_404(document_qs, id=document_id)
        return document.scans.filter(id=scan_id)


class Transcript(BaseDetailView):
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer

    def get_object(self, queryset=None):
        transcript_qs = self.get_queryset()\
            .select_related('document__project')\
            .filter(
                document__id=self.kwargs.get('document_id'),
                document__project__slug=self.kwargs.get('project_slug')
            )
        return get_object_or_404(transcript_qs)
