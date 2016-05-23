from pyld import jsonld

from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

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
    allowed_methods = ('GET', 'DELETE',)

    def put(self, *args, **kwargs):
        raise MethodNotAllowed()

    def finalize_response(self, request, *args, **kwargs):
        response = super(TopicDetail, self).finalize_response(request, *args, **kwargs)

        if request.method == 'GET':
            hydra_class = self.get_hydra_class(request)

            wn_aspect = next(
                p for p in hydra_class['hydra:supportedProperty']
                if p['hydra:title'] == 'wn_aspect'
            )['property']

            project_aspect = next(
                p for p in hydra_class['hydra:supportedProperty']
                if p['hydra:title'] == 'project_aspect'
            )['property']

            response.data['embedded'][wn_aspect['@id']] = wn_aspect
            response.data['embedded'][project_aspect['@id']] = project_aspect

            # Add hydra links for different aspects
            response.data['@context'] = {
                'wn_aspect': {
                    '@type': '@id',
                    '@id': wn_aspect['@id'],
                },
                'project_aspect': {
                    '@type': '@id',
                    '@id': project_aspect['@id'],
                }
            }


            # Change @context to point aspects toward links

        return response


class TopicConfirmDelete(DeleteConfirmAPIView):
    queryset = Topic.objects.all()
    permissions = {
        'GET': ('main.delete_topic',),
        'HEAD': ('main.delete_topic',)
    }


class ENTopicDetail(BaseDetailView):
    queryset = Topic.objects.all()
    serializer_class = ENTopicSerializer
    permissions = {
        'PUT': (
            # FIXME: make this change_wn_aspect
            'main.change_topic',
        )
    }
    allowed_methods = ('GET', 'PUT',)


class TopicLDDetail(ProjectSpecificMixin, GenericAPIView):
    queryset = Topic.objects.all()
    permission_classes = (ProjectSpecificPermissions,)
    permissions = {
        'PUT': (
            # FIXME: make this change_project_aspect
            'main.change_topic',
        )
    }
    allowed_methods = ('GET', 'PUT',)

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
