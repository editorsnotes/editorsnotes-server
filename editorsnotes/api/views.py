from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

import serializers
from permissions import ProjectSpecificPermission
from editorsnotes.main.models import Topic, Note, Document

class BaseListAPIView(generics.ListCreateAPIView):
    paginate_by = 50
    paginate_by_param = 'page_size'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    def pre_save(self, obj):
        obj.creator = obj.last_updater = self.request.user

class BaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    def pre_save(self, obj):
        obj.last_updater = self.request.user

########

@api_view(('GET',))
def root(request):
    return Response({
        'auth-token': reverse('obtain-auth-token'),
        'notes': reverse('api-notes-list'),
        'topics': reverse('api-topics-list'),
        'documents': reverse('api-documents-list')
    })

########

class TopicList(BaseListAPIView):
    model = Topic
    serializer_class = serializers.TopicSerializer

class TopicDetail(BaseDetailView):
    model = Topic
    serializer_class = serializers.TopicSerializer

########

class NoteList(BaseListAPIView):
    model = Note
    serializer_class = serializers.MinimalNoteSerializer

class NoteDetail(BaseDetailView):
    model = Note
    serializer_class = serializers.NoteSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, ProjectSpecificPermission)
    def post(self, request, *args, **kwargs):
        """Add a note section"""
        raise NotImplementedError()

########

class DocumentList(BaseListAPIView):
    model = Document
    serializer_class = serializers.DocumentSerializer

class DocumentDetail(BaseDetailView):
    model = Document
    serializer_class = serializers.DocumentSerializer
