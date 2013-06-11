from editorsnotes.main.models.documents import Document

from .base import BaseListAPIView, BaseDetailView
from ..serializers import DocumentSerializer

class DocumentList(BaseListAPIView):
    model = Document
    serializer_class = DocumentSerializer
    def pre_save(self, obj):
        super(DocumentList, self).save(obj)
        obj.project = self.request.project

class DocumentDetail(BaseDetailView):
    model = Document
    serializer_class = DocumentSerializer
