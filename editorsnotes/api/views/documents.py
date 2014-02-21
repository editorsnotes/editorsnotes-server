from editorsnotes.main.models import Document

from .base import (BaseListAPIView, BaseDetailView, CreateReversionMixin,
                   ElasticSearchRetrieveMixin, ElasticSearchListMixin)
from ..serializers import DocumentSerializer

class DocumentList(CreateReversionMixin, ElasticSearchListMixin, BaseListAPIView):
    model = Document
    serializer_class = DocumentSerializer

class DocumentDetail(BaseDetailView, CreateReversionMixin):
    model = Document
    serializer_class = DocumentSerializer
