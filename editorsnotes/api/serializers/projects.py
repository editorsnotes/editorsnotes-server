from rest_framework import serializers
from rest_framework.reverse import reverse

from editorsnotes.main.models import Project
from editorsnotes.search import get_index

from .base import URLField

def count_for(project, doc_type):
    index = get_index('main')
    count = index.es.count(
        { 'query': { 'term': { 'serialized.project.name': project.name }}},
        index=index.name,
        doc_type=doc_type)
    return count['count']


class ProjectSerializer(serializers.ModelSerializer):
    url = URLField('api:api-projects-detail', ('slug',))
    notes = serializers.SerializerMethodField()
    notes_url = URLField('api:api-notes-list', ('slug',))
    topics = serializers.SerializerMethodField()
    topics_url = URLField('api:api-topics-list', ('slug',))
    documents = serializers.SerializerMethodField()
    documents_url = URLField('api:api-documents-list', ('slug',))
    activity_url = URLField('api:api-projects-activity', ('slug',))
    class Meta:
        model = Project
        fields = ('slug', 'url', 'name', 'description', 'notes', 'notes_url',
                  'topics', 'topics_url', 'documents', 'documents_url', 'activity_url')
    def get_notes(self, obj):
        return count_for(obj, 'note')
    def get_topics(self, obj):
        return count_for(obj, 'topic')
    def get_documents(self, obj):
        return count_for(obj, 'document')
