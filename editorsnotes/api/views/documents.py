from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser

from editorsnotes.main.models import Document, Scan

from .base import BaseListAPIView, BaseDetailView, ElasticSearchListMixin
from ..serializers import DocumentSerializer, ScanSerializer

__all__ = ['DocumentList', 'DocumentDetail', 'ScanList', 'ScanDetail',
           'normalize_scan_order']

class DocumentList(ElasticSearchListMixin, BaseListAPIView):
    model = Document
    serializer_class = DocumentSerializer

class DocumentDetail(BaseDetailView):
    model = Document
    serializer_class = DocumentSerializer

def normalize_scan_order(request, project_slug, document_id):
    document_qs = Document.objects.select_related('scans')
    document = get_object_or_404(document_qs, id=document_id)
    can_edit = (request.user and
                request.user.has_project_perm(document.project, 'main.change_document'))
    if not can_edit:
        raise HttpResponseForbidden('You do not have permissions to perform this action.')
    step = int(request.GET.get('step', 100))
    document.scans.normalize_ordering_values('ordering', step=step, fill_in_empty=True)
    return HttpResponse()

class ScanList(BaseListAPIView):
    model = Scan
    serializer_class = ScanSerializer
    parser_classes = (MultiPartParser,)
    def get_document(self):
        document_id = self.kwargs.get('document_id')
        document_qs = Document.objects.select_related('scans')
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
        document_qs = Document.objects.select_related('scans')
        document = get_object_or_404(document_qs, id=document_id)
        return document.scans.filter(id=scan_id)
