from django.contrib.contenttypes.models import ContentType

from rest_framework.relations import RelatedField
from rest_framework.serializers import Field, ModelSerializer
import reversion

from editorsnotes.main.models.topics import (
    ProjectTopicContainer, TopicNodeAssignment)

class URLField(Field):
    read_only = True
    def field_to_native(self, obj, field_name):
        return obj.get_absolute_url()

class ProjectSlugField(Field):
    read_only = True
    def field_to_native(self, obj, field_name):
        project = obj.get_affiliation()
        return project.slug

class TopicAssignmentField(RelatedField):
    def __init__(self, *args, **kwargs):
        super(TopicAssignmentField, self).__init__(*args, **kwargs)
        self.many = True
    def field_to_native(self, obj, field_name):
        return [{'name': ta.container.preferred_name,
                 'url': ta.container.get_absolute_url()}
                for ta in obj.topics.all()]
    def field_from_native(self, data, files, field_name, into):
        if self.read_only:
            return
        into[field_name] = data.get(field_name, [])

class ReversionSerializerMixin(object):
    def save_object(self, *args, **kwargs):
        _save_object = super(ReversionSerializerMixin, self).save_object
        if self.context.get('create_revision', False):
            with reversion.create_revision():
                saved = _save_object(*args, **kwargs)
        else:
            saved = _save_object(*args, **kwargs)
        return saved

class RelatedTopicModelSerializer(ModelSerializer):
    topics = TopicAssignmentField(read_only=False)
    def save_related_topics(self, obj, topics):
        """
        Given an array of names, make sure obj is related to those topics.
        """
        to_create = topics[:]
        to_delete = []

        for assignment in obj.topics.select_related('container').all():
            topic_name = assignment.container.preferred_name
            if topic_name in topics:
                to_create.remove(topic_name)
            else:
                to_delete.append(assignment)

        for assignment in to_delete:
            assignment.delete()

        user = self.context['request'].user
        project = self.context['request'].project

        for topic_name in to_create:
            container = ProjectTopicContainer.objects.get_or_create_by_name(
                topic_name, project, user)
            obj.topics.create(container=container, creator_id=user.id)

    def save_object(self, obj, **kwargs):
        # Need to change to allow partial updates, etc.
        topics = []
        if getattr(obj, '_m2m_data', None):
            topics = obj._m2m_data.pop('topics')
        super(RelatedTopicModelSerializer, self).save_object(obj, **kwargs)
        self.save_related_topics(obj, topics)
