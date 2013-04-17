from django.http import Http404
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

import serializers
from permissions import ProjectSpecificPermission
from editorsnotes.main.models import Topic, Note, Document, NoteSection

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
    def post(self, request, format=None):
        """Add a new note section"""
        section_type = request.DATA.get('section_type', None)
        if section_type is None:
            raise Exception('need a section type')

        if section_type == 'citation':
            sec_serializer = serializers.CitationNSSerializer
        elif section_type == 'text':
            sec_serializer = serializers.TextNSSerializer
        elif section_type == 'note_reference':
            sec_serializer = serializers.NoteReferenceNSSerializer
        else:
            raise NotImplementedError('invalid section type')

        serializer = sec_serializer(request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serialzer.data, status=status.HTTP_400_BAD_REQUEST)


class NoteSectionDetail(BaseDetailView):
    def get_object(self, queryset=None):
        if queryset is None:
            raise Exception
        obj = queryset.get()
        self.check_object_permissions(self.request, obj)
        return obj
    def get_queryset(self):
        note_id = self.kwargs.get('note_id')
        section_id = self.kwargs.get('section_id')
        note = Note.objects.get(id=note_id)
        qs = note.sections.select_subclasses()\
                .filter(note_section_id=section_id)
        if qs.count() != 1:
            raise Http404()
        self.model = qs[0].__class__
        return qs
    def get_serializer_class(self):
        section_type = getattr(self.object, 'section_type', '')
        if section_type == 'citation':
            return serializers.CitationNSSerializer
        elif section_type == 'text':
            return serializers.TextNSSerializer
        elif section_type == 'note_reference':
            return serializers.NoteReferenceNSSerializer
        else:
            raise Exception

########

class DocumentList(BaseListAPIView):
    model = Document
    serializer_class = serializers.DocumentSerializer

class DocumentDetail(BaseDetailView):
    model = Document
    serializer_class = serializers.DocumentSerializer
