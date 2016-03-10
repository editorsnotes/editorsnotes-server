from editorsnotes.main.models import Topic

from .. import filters as es_filters
from ..serializers.topics import TopicSerializer, ENTopicSerializer

from .base import BaseListAPIView, BaseDetailView, DeleteConfirmAPIView
from .mixins import (ElasticSearchListMixin, EmbeddedReferencesMixin,
                     HydraAffordancesMixin)

__all__ = [
    'TopicList',
    'TopicDetail',
    'ENTopicDetail',
    'TopicConfirmDelete'
]


class TopicList(ElasticSearchListMixin, BaseListAPIView):
    queryset = Topic.objects.all()
    es_filter_backends = (
        es_filters.ProjectFilterBackend,
        es_filters.QFilterBackend,
        es_filters.UpdaterFilterBackend,
    )
    hydra_project_perms = ('main.add_topic',)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ENTopicSerializer
        return TopicSerializer

    def create(self, *args, **kwargs):
        resp = super(TopicList, self).create(*args, **kwargs)
        resp.data = None
        return resp


class TopicDetail(EmbeddedReferencesMixin, HydraAffordancesMixin,
                  BaseDetailView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    hydra_project_perms = ('main.change_topic', 'main.delete_topic',)


class ENTopicDetail(EmbeddedReferencesMixin, HydraAffordancesMixin,
                    BaseDetailView):
    queryset = Topic.objects.all()
    serializer_class = ENTopicSerializer
    hydra_project_perms = ('main.change_topic', 'main.delete_topic',)


class TopicConfirmDelete(DeleteConfirmAPIView):
    queryset = Topic.objects.all()
    permissions = {
        'GET': ('main.delete_topic',),
        'HEAD': ('main.delete_topic',)
    }
