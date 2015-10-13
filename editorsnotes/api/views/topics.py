import json

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from editorsnotes.main.models import Topic

from .base import (BaseListAPIView, BaseDetailView, DeleteConfirmAPIView,
                   ElasticSearchListMixin, ProjectSpecificMixin,
                   ProjectSpecificPermissions, create_revision_on_methods,
                   LinkerMixin, EmbeddedMarkupReferencesMixin)
from ..linkers import (AddProjectObjectLinker, EditProjectObjectLinker,
                       DeleteProjectObjectLinker)
from ..serializers.topics import TopicSerializer

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
