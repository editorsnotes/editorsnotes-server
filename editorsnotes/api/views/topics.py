import json

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from editorsnotes.main.models import Topic, TopicNode, Citation
from editorsnotes.main.models.topics import TYPE_CHOICES

from .base import (BaseListAPIView, BaseDetailView, DeleteConfirmAPIView,
                   ElasticSearchListMixin, ProjectSpecificMixin,
                   ProjectSpecificPermissions, create_revision_on_methods,
                   LinkerMixin)
from ..linkers import (AddProjectObjectLinker, EditProjectObjectLinker,
                       DeleteProjectObjectLinker)
from ..serializers.topics import TopicSerializer, TopicNodeSerializer
from ..serializers.documents import CitationSerializer

__all__ = ['TopicNodeList', 'TopicNodeDetail', 'TopicList', 'TopicDetail',
           'TopicConfirmDelete', 'TopicCitationList', 'TopicCitationDetail',
           'NormalizeCitationOrder']

def topic_types(request):
    types = { 'types': [{'key': key, 'localized': localized}
                        for key, localized in TYPE_CHOICES] }
    return HttpResponse(json.dumps(types), content_type="application/json")

class NormalizeCitationOrder(ProjectSpecificMixin, APIView):
    """
    Normalize the order of a document's scans. Items will remain in the same
    order, but their `ordering` property will be equally spaced out.

    @param step: integer indicating the step between each ordering value.
    Default 100.
    """
    parser_classes = (JSONParser,)
    permission_classes = (ProjectSpecificPermissions,)
    permissions = {
        'POST': ('main.change_topic',)
    }
    def get_object(self):
        qs = Topic.objects\
                .filter(project__id=self.request.project.id,
                        topic_node_id=self.kwargs.get('topic_node_id'))\
                .prefetch_related('summary_cites')
        return get_object_or_404(qs)
    def post(self, request, *args, **kwargs):
        topic = self.get_object()
        self.check_object_permissions(self.request, topic)
        step = int(request.GET.get('step', 100))
        topic.summary_cites.normalize_ordering_values('ordering', step=step, fill_in_empty=True)
        return Response()


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
class TopicDetail(BaseDetailView, CreateModelMixin):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    linker_classes = (EditProjectObjectLinker, DeleteProjectObjectLinker,)
    def get_object(self, queryset=None):
        # TODO: Make sure permissions are in fact checked
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
    queryset = Citation.objects.all()
    serializer_class = CitationSerializer
    def pre_save(self, obj):
        obj.content_type = ContentType.objects.get_for_model(Topic)
        obj.object_id = self.get_topic().id
        super(TopicCitationList, self).pre_save(obj)

class TopicCitationDetail(CitationMixin, BaseDetailView):
    queryset = Citation.objects.all()
    serializer_class = CitationSerializer
    def get_object(self, queryset=None):
        qs = self.get_queryset()
        return get_object_or_404(qs, id=self.kwargs['citation_id'])
