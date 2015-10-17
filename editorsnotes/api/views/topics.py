from editorsnotes.main.models import Topic

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
