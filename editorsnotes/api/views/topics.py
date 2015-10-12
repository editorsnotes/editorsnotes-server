import json

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from editorsnotes.main.models import Topic, TopicNode
from editorsnotes.main.models.topics import TYPE_CHOICES

from .base import (BaseListAPIView, BaseDetailView, DeleteConfirmAPIView,
                   ElasticSearchListMixin, ProjectSpecificMixin,
                   ProjectSpecificPermissions, create_revision_on_methods,
                   LinkerMixin, EmbeddedMarkupReferencesMixin)
from ..linkers import (AddProjectObjectLinker, EditProjectObjectLinker,
                       DeleteProjectObjectLinker, ReferencedByLinker)
from ..serializers.topics import TopicSerializer, TopicNodeSerializer

__all__ = ['TopicNodeList', 'TopicNodeDetail', 'TopicList', 'TopicDetail',
           'TopicConfirmDelete']

def topic_types(request):
    types = { 'types': [{'key': key, 'localized': localized}
                        for key, localized in TYPE_CHOICES] }
    return HttpResponse(json.dumps(types), content_type="application/json")

class TopicNodeList(ListAPIView):
    paginate_by = 50
    paginate_by_param = 'page_size'
    queryset = TopicNode.objects.all()
    serializer_class = TopicNodeSerializer

class TopicNodeDetail(RetrieveAPIView):
    queryset = TopicNode.objects.all()
    serializer_class = TopicNodeSerializer

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
    def get_object(self):
        qs = self.model.objects.filter(project=self.request.project,
                                       topic_node_id=self.kwargs['topic_node_id'])
        obj = get_object_or_404(qs)
        self.check_object_permissions(self.request, obj)
        return obj

@create_revision_on_methods('create')
class TopicDetail(EmbeddedMarkupReferencesMixin, BaseDetailView,
                  CreateModelMixin):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    linker_classes = (EditProjectObjectLinker, DeleteProjectObjectLinker,
                      ReferencedByLinker)
    def get_object(self, queryset=None):
        # TODO: Make sure permissions are in fact checked
        filtered_queryset = self.filter_queryset(self.get_queryset())
        return get_object_or_404(filtered_queryset,
                                 project=self.request.project,
                                 topic_node_id=self.kwargs['topic_node_id'])
