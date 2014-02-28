from django.shortcuts import get_object_or_404

from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView

from editorsnotes.main.models import Topic, TopicNode

from .base import (BaseListAPIView, BaseDetailView, ElasticSearchListMixin,
                   create_revision_on_methods)
from ..serializers.topics import TopicSerializer, TopicNodeSerializer

__all__ = ['TopicNodeList', 'TopicNodeDetail', 'TopicList', 'TopicDetail']

class TopicNodeList(ListAPIView):
    model = TopicNode
    serializer_class = TopicNodeSerializer

class TopicNodeDetail(RetrieveAPIView):
    model = TopicNode
    serializer_class = TopicNodeSerializer

class TopicList(ElasticSearchListMixin, BaseListAPIView):
    model = Topic
    serializer_class = TopicSerializer

@create_revision_on_methods('create')
class TopicDetail(BaseDetailView, CreateModelMixin):
    model = Topic
    serializer_class = TopicSerializer
    def get_object(self, queryset=None):
        filtered_queryset = self.filter_queryset(self.get_queryset())
        return get_object_or_404(filtered_queryset,
                                 project=self.request.project,
                                 topic_node_id=self.kwargs['topic_node_id'])
