from editorsnotes.main.models import Topic

from .. import filters as es_filters
from ..serializers.topics import TopicSerializer

from .base import BaseListAPIView, BaseDetailView, DeleteConfirmAPIView
from .mixins import (ElasticSearchListMixin, EmbeddedMarkupReferencesMixin,
                     EmbeddedHydraClassMixin)

__all__ = ['TopicList', 'TopicDetail', 'TopicConfirmDelete']


class TopicList(ElasticSearchListMixin, BaseListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    es_filter_backends = (
        es_filters.ProjectFilterBackend,
        es_filters.QFilterBackend,
        es_filters.UpdaterFilterBackend,
    )
    hydra_project_perms = ('main.add_topic',)


class TopicDetail(EmbeddedMarkupReferencesMixin, EmbeddedHydraClassMixin,
                  BaseDetailView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    hydra_project_perms = ('main.change_topic', 'main.delete_topic',)


class TopicConfirmDelete(DeleteConfirmAPIView):
    queryset = Topic.objects.all()
    permissions = {
        'GET': ('main.delete_topic',),
        'HEAD': ('main.delete_topic',)
    }
