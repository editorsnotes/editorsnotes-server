from django.core.urlresolvers import reverse
from rest_framework import serializers

from editorsnotes.main.models import Project

class ProjectSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_api_url')
    notes = serializers.SerializerMethodField('get_notes_url')
    topics = serializers.SerializerMethodField('get_topics_url')
    documents = serializers.SerializerMethodField('get_documents_url')
    class Meta:
        model = Project
        fields = ('slug', 'name', 'url', 'notes', 'topics', 'documents',)
    def get_api_url(self, obj):
        return reverse('api:api-project-detail', args=(obj.slug,))
    def get_notes_url(self, obj):
        return reverse('api:api-notes-list', args=(obj.slug,))
    def get_topics_url(self, obj):
        return reverse('api:api-topics-list', args=(obj.slug,))
    def get_documents_url(self, obj):
        return reverse('api:api-documents-list', args=(obj.slug,))
