from editorsnotes.main.models.topics import Topic

from .base import BaseListAPIView, BaseDetailView
from ..serializers import TopicSerializer

class TopicList(BaseListAPIView):
    model = Topic
    serializer_class = TopicSerializer

class TopicDetail(BaseDetailView):
    model = Topic
    serializer_class = TopicSerializer

