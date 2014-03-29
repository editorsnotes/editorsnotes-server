from django.shortcuts import get_object_or_404

from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView

from editorsnotes.main.models import Topic, TopicNode, Citation

from .base import (BaseListAPIView, BaseDetailView, ElasticSearchListMixin,
                   create_revision_on_methods)
from ..serializers.topics import TopicSerializer, TopicNodeSerializer
from ..serializers.documents import CitationSerializer

__all__ = ['TopicNodeList', 'TopicNodeDetail', 'TopicList', 'TopicDetail',
           'TopicCitationList', 'TopicCitationDetail']

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

class CitationMixin(object):
    def get_topic(self):
        if not hasattr(self, '_topic'):
            self._topic = Topic.objects.get(topic_node_id=self.kwargs['topic_node_id'],
                                            project_id=self.request.project.id)
        return self._topic
    def get_queryset(self):
        topic = self.get_topic()
        return Citation.objects.get_for_object(topic)

class TopicCitationList(CitationMixin, BaseListAPIView):
    model = Citation
    serializer_class = CitationSerializer
    def pre_save(self, obj):
        obj.content_obj = self.get_topic()
        super(TopicCitationList, self).pre_save(obj)

class TopicCitationDetail(CitationMixin, BaseDetailView):
    model = Citation
    serializer_class = CitationSerializer
    def get_object(self, queryset=None):
        qs = self.get_queryset()
        return get_object_or_404(qs, id=self.kwargs['citation_id'])
