from rest_framework import serializers
from rest_framework.reverse import reverse

from editorsnotes.auth.models import Project, User, FeaturedItem, ProjectRole
from editorsnotes.search import get_index

from .base import URLField

__all__ = ['ProjectSerializer', 'MinimalUserSerializer', 'UserSerializer']

def count_for(project, doc_type):
    index = get_index('main')
    count = index.es.count(
        { 'query': { 'term': { 'serialized.project.name': project.name }}},
        index=index.name,
        doc_type=doc_type)
    return count['count']

class FeaturedItemSerializer(serializers.ModelSerializer):
    item_url = serializers.SerializerMethodField()
    item_title = serializers.ReadOnlyField(source='content_object.as_text')
    item_type = serializers.ReadOnlyField(source='content_object._meta.model_name')
    class Meta:
        model = FeaturedItem
        fields = ('item_url', 'item_title', 'item_type',)
    def get_item_url(self, obj):
        url = obj.content_object.get_absolute_url()
        return self.context['request'].build_absolute_uri(url)


class ProjectSerializer(serializers.ModelSerializer):
    url = URLField('api:projects-detail', {'project_slug': 'slug'})
    featured_items = FeaturedItemSerializer(many=True, source='featureditem_set')
    notes = serializers.SerializerMethodField()
    notes_url = URLField('api:notes-list', {'project_slug': 'slug'})
    topics = serializers.SerializerMethodField()
    topics_url = URLField('api:topics-list', {'project_slug': 'slug'})
    documents = serializers.SerializerMethodField()
    documents_url = URLField('api:documents-list', {'project_slug': 'slug'})
    activity_url = URLField('api:projects-activity', {'project_slug': 'slug'})
    class Meta:
        model = Project
        fields = ('slug', 'url', 'name', 'description', 'featured_items', 'notes', 'notes_url',
                  'topics', 'topics_url', 'documents', 'documents_url', 'activity_url')
    def get_notes(self, obj):
        return count_for(obj, 'note')
    def get_topics(self, obj):
        return count_for(obj, 'topic')
    def get_documents(self, obj):
        return count_for(obj, 'document')

class MinimalUserSerializer(serializers.ModelSerializer):
    url = URLField('api:users-detail', {'username': 'username'})
    class Meta:
        model = User
        fields = ('url', 'display_name')

class ProjectRoleSerializer(serializers.ModelSerializer):
    project = serializers.ReadOnlyField(source='project.name')
    project_url = URLField('api:projects-detail', {'project_slug': 'project.slug' })
    class Meta:
        model = ProjectRole
        fields = ('project', 'project_url', 'role',)


class UserSerializer(serializers.ModelSerializer):
    url = URLField('api:users-detail', {'username': 'username'})
    project_roles = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('username', 'url', 'display_name', 'project_roles',)
    def get_project_roles(self, obj):
        roles = [role for project, role in obj.get_affiliated_projects_with_roles()]
        return ProjectRoleSerializer(roles, many=True, context=self.context).data