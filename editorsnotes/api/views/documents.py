from editorsnotes.main.models import Document

from .base import (BaseListAPIView, BaseDetailView, ElasticSearchRetrieveMixin,
                   ElasticSearchListMixin)
from ..serializers import DocumentSerializer

class DocumentList(ElasticSearchListMixin, BaseListAPIView):
    model = Document
    serializer_class = DocumentSerializer

class DocumentDetail(BaseDetailView):
    model = Document
    serializer_class = DocumentSerializer
