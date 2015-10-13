from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.reverse import reverse

from editorsnotes.main.models import Topic, TopicNode

from ..fields import (CurrentProjectDefault, ProjectSlugField,
                      TopicAssignmentField, IdentityURLField)
from ..validators import UniqueToProjectValidator

from .base import EmbeddedMarkupReferencesMixin, RelatedTopicSerializerMixin


__all__ = ['TopicSerializer', 'TopicNodeSerializer']


class TopicNodeSerializer(serializers.ModelSerializer):
    name = ReadOnlyField(source='_preferred_name')
    url = IdentityURLField()
    alternate_forms = serializers.SerializerMethodField('get_alternate_forms')
    project_topics = serializers.SerializerMethodField('get_project_value')

    class Meta:
        model = TopicNode
        fields = ('id', 'name', 'url', 'alternate_forms', 'type',
                  'project_topics',)

    def get_alternate_forms(self, obj):
        topics = obj.project_topics.select_related('alternate_names')
        alternate_forms = set()
        alternate_forms.update(topic.preferred_name for topic in topics)
        alternate_forms.update(
            alternate_name.name
            for topic in topics
            for alternate_name in topic.alternate_names.all())
        alternate_forms.remove(obj._preferred_name)
        return list(alternate_forms)

    def get_project_value(self, obj):
        return [OrderedDict((
            ('project_name', topic.project.name),
            ('project_url', reverse('api:projects-detail',
                                    request=self.context['request'],
                                    kwargs={
                                        'project_slug': topic.project.slug
                                    })),
            ('preferred_name', topic.preferred_name),
            ('url', reverse('api:topics-detail',
                            request=self.context['request'],
                            kwargs={
                                'project_slug': topic.project.slug,
                                'pk': obj.id
                            }))
        ))
            for topic in obj.project_topics.select_related('project')]


class AlternateNameField(serializers.Field):
    def to_representation(self, value):
        return value.values_list('name', flat=True)

    def to_internal_value(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('Alternate names must be a list')
        if not all([1 <= len(name) <= 200 for name in value]):
            raise serializers.ValidationError(
                'Alternate names must be between 1 and 200 characters.')
        return value


class TopicSerializer(EmbeddedMarkupReferencesMixin,
                      RelatedTopicSerializerMixin,
                      serializers.ModelSerializer):
    topic_node_id = ReadOnlyField(source='topic_node.id')
    type = ReadOnlyField(source='topic_node.type')
    alternate_names = AlternateNameField(required=False)
    url = IdentityURLField()
    project = ProjectSlugField(default=CurrentProjectDefault())
    related_topics = TopicAssignmentField(required=False)

    class Meta:
        model = Topic
        fields = ('id', 'topic_node_id', 'preferred_name', 'type',
                  'url', 'alternate_names', 'related_topics', 'project',
                  'last_updated', 'markup', 'markup_html')
        validators = [
            UniqueToProjectValidator('preferred_name')
        ]

    def __init__(self, *args, **kwargs):
        minimal = kwargs.pop('minimal', False)
        super(TopicSerializer, self).__init__(*args, **kwargs)
        if minimal:
            self.fields.pop('markup')
            self.fields.pop('markup_html')
            self.fields.pop('_embedded', None)

    def create(self, validated_data):
        topic_node_id = self.context.get('topic_node_id', None)
        if topic_node_id is None and 'view' in self.context:
            topic_node_id = self.context['view'].kwargs.get(
                'topic_node_id', None)
        if topic_node_id is None:
            topic_node = TopicNode.objects.create(
                _preferred_name=validated_data['preferred_name'],
                creator=validated_data['creator'],
                last_updater=validated_data['last_updater'])
            topic_node_id = topic_node.id
        validated_data['topic_node_id'] = topic_node_id
        alternate_names = validated_data.pop('alternate_names', None)
        instance = super(TopicSerializer, self).create(validated_data)
        self.save_alternate_names(instance, alternate_names)
        return instance

    def update(self, instance, validated_data):
        alternate_names = validated_data.pop('alternate_names', None)
        instance = super(TopicSerializer, self)\
            .update(instance, validated_data)
        self.save_alternate_names(instance, alternate_names)
        return instance

    def save_alternate_names(self, obj, alternate_names):
        if alternate_names is None:
            return
        to_create = set(alternate_names)
        to_delete = []

        queryset = obj.alternate_names.all()
        for alternate_name_obj in queryset:
            name = alternate_name_obj.name
            if name in alternate_names:
                to_create.remove(name)
            else:
                to_delete.append(alternate_name_obj)

        for alternate_name_obj in to_delete:
            alternate_name_obj.delete()

        user = self.context['request'].user
        for name in to_create:
            obj.alternate_names.create(name=name, creator_id=user.id)
