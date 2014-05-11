from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser

from editorsnotes.main.models import Document, Scan

from .base import (BaseListAPIView, BaseDetailView, ElasticSearchRetrieveMixin,
                   ElasticSearchListMixin)
from ..serializers import DocumentSerializer, ScanSerializer

__all__ = ['DocumentList', 'DocumentDetail', 'ScanList', 'ScanDetail']

class DocumentList(ElasticSearchListMixin, BaseListAPIView):
    model = Document
    serializer_class = DocumentSerializer

class DocumentDetail(BaseDetailView):
    model = Document
    serializer_class = DocumentSerializer

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
