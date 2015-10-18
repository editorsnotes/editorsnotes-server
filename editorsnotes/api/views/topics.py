from editorsnotes.main.models import Topic

from .. import filters as es_filters
from ..linkers import (AddProjectObjectLinker, EditProjectObjectLinker,
                       DeleteProjectObjectLinker)
from ..serializers.topics import TopicSerializer

from .base import BaseListAPIView, BaseDetailView, DeleteConfirmAPIView
from .mixins import (ElasticSearchListMixin, EmbeddedMarkupReferencesMixin,
                     LinkerMixin)

__all__ = ['TopicList', 'TopicDetail', 'TopicConfirmDelete']


class TopicList(ElasticSearchListMixin, LinkerMixin, BaseListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    linker_classes = (AddProjectObjectLinker,)
    es_filter_backends = (
        es_filters.ProjectFilterBackend,
        es_filters.QFilterBackend,
        es_filters.UpdaterFilterBackend,
    )


class TopicConfirmDelete(DeleteConfirmAPIView):
    queryset = Topic.objects.all()
    permissions = {
        'GET': ('main.delete_topic',),
        'HEAD': ('main.delete_topic',)
    }


class TopicDetail(EmbeddedMarkupReferencesMixin, BaseDetailView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    linker_classes = (EditProjectObjectLinker, DeleteProjectObjectLinker)
