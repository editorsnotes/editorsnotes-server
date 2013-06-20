from django.contrib.contenttypes.models import ContentType

from rest_framework.relations import RelatedField
from rest_framework.serializers import ModelSerializer 

from editorsnotes.main.models.topics import (
    ProjectTopicContainer, TopicNodeAssignment)

class TopicAssignmentField(RelatedField):
    def __init__(self, *args, **kwargs):
        super(TopicAssignmentField, self).__init__(*args, **kwargs)
        self.many = True
    def field_to_native(self, obj, field_name):
        ct = ContentType.objects.get_for_model(obj)
        qs = ProjectTopicContainer.objects\
                .select_related('project')\
                .filter(related_topics__content_type_id=ct.id,
                        related_topics__object_id=obj.id)
        return [{'name': t.preferred_name, 'url': t.get_absolute_url()}
                for t in qs]
    def field_from_native(self, data, files, field_name, into):
        if self.read_only:
            return
        into[field_name] = data.get(field_name, [])

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
