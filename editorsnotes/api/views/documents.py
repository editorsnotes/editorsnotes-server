from editorsnotes.main.models.documents import Document

from .base import BaseListAPIView, BaseDetailView
from ..serializers import DocumentSerializer

class DocumentList(BaseListAPIView):
    model = Document
    serializer_class = DocumentSerializer

class DocumentDetail(BaseDetailView):
    model = Document
    serializer_class = DocumentSerializer
