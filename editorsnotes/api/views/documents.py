from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from editorsnotes.main.models import Document, Scan

from .base import (BaseListAPIView, BaseDetailView, DeleteConfirmAPIView,
                   ElasticSearchListMixin, ProjectSpecificMixin)
from ..permissions import ProjectSpecificPermissions
from ..serializers import DocumentSerializer, ScanSerializer

__all__ = ['DocumentList', 'DocumentDetail', 'DocumentConfirmDelete',
           'ScanList', 'ScanDetail', 'NormalizeScanOrder']

class DocumentList(ElasticSearchListMixin, BaseListAPIView):
    model = Document
    serializer_class = DocumentSerializer

class DocumentDetail(BaseDetailView):
    model = Document
    serializer_class = DocumentSerializer

class DocumentConfirmDelete(DeleteConfirmAPIView):
    model = Document
    permissions = {
        'GET': ('main.delete_document',),
        'HEAD': ('main.delete_document',)
    }

class NormalizeScanOrder(ProjectSpecificMixin, APIView):
    """
    Normalize the order of a document's scans. Items will remain in the same
    order, but their `ordering` property will be equally spaced out.

    @param step: integer indicating the step between each ordering value.
    Default 100.
    """
    parser_classes = (JSONParser,)
    permission_classes = (ProjectSpecificPermissions,)
    permissions = {
        'POST': ('main.change_document',)
    }
    def get_object(self):
        qs = Document.objects\
                .filter(project__id=self.request.project.id,
                        id=self.kwargs.get('document_id'))\
                .select_related('scans')
        return get_object_or_404(qs)
    def post(self, request, *args, **kwargs):
        document = self.get_object()
        self.check_object_permissions(self.request, document)
        step = int(request.GET.get('step', 100))
        document.scans.normalize_ordering_values('ordering', step=step, fill_in_empty=True)
        return Response([
            { 'id': _id, 'ordering': ordering }
            for _id, ordering in document.scans.values_list('id', 'ordering')
        ])

class ScanList(BaseListAPIView):
    model = Scan
    serializer_class = ScanSerializer
    parser_classes = (MultiPartParser,)
    paginate_by = None
    def get_document(self):
        document_id = self.kwargs.get('document_id')
        document_qs = Document.objects.prefetch_related('scans__creator')
        document = get_object_or_404(document_qs, id=document_id)
        return document
    def get_queryset(self):
        return self.get_document().scans.all()
    def pre_save(self, obj):
        super(ScanList, self).pre_save(obj)
        obj.document = self.get_document()
        return obj


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
