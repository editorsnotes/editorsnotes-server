from pyld import jsonld

from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from editorsnotes.main.models import Topic

from .. import filters as es_filters
from ..permissions import ProjectSpecificPermissions
from ..serializers.topics import TopicSerializer, ENTopicSerializer

from .base import BaseListAPIView, BaseDetailView, DeleteConfirmAPIView
from .mixins import (ElasticSearchListMixin, EmbeddedReferencesMixin,
                     ProjectSpecificMixin, HydraAffordancesMixin)

__all__ = [
    'TopicList',
    'TopicDetail',
    'ENTopicDetail',
    'TopicLDDetail',
    'TopicConfirmDelete',
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


class ENTopicDetail(BaseDetailView):
    queryset = Topic.objects.all()
    serializer_class = ENTopicSerializer


class TopicConfirmDelete(DeleteConfirmAPIView):
    queryset = Topic.objects.all()
    permissions = {
        'GET': ('main.delete_topic',),
        'HEAD': ('main.delete_topic',)
    }


class TopicLDDetail(ProjectSpecificMixin, GenericAPIView):
    permission_classes = (ProjectSpecificPermissions,)
    permissions = {
        'PUT': ('main.change_topic',)
    }
    queryset = Topic.objects.all()

    def get(self, request, **kwargs):
        topic = self.get_object()
        return Response(topic.ld)

    def put(self, request, **kwargs):
        data = request.data
        topic = self.get_object()

        url = request.build_absolute_uri(topic.get_absolute_url())
        framed = jsonld.frame(data, {'@id': url})
        topic.ld = framed['@graph'][0] if framed['@graph'] else {}

        # TODO: make revision
        topic.save()

        return Response(topic.ld)
