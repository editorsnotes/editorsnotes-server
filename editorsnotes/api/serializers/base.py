from django.core.urlresolvers import NoReverseMatch
from rest_framework.relations import (HyperlinkedRelatedField, RelatedField,
                                      get_attribute)
from rest_framework.reverse import reverse
from rest_framework.serializers import ReadOnlyField

from editorsnotes.main.models import Topic, TopicAssignment, Project

def nested_getattr(obj, attr_string):
    for attr in attr_string.split('.'):
        obj = getattr(obj, attr)
    return obj

class CurrentProjectDefault:
    def set_context(self, serializer_field):
        self.project = serializer_field.context['request'].project

    def __call__(self):
        return self.project

    def __repr__(self):
        return u'%s()' % self.__class__.__name__

class URLField(ReadOnlyField):
    """
    An identity URL field.

    lookup_arg_attrs should be an iterable of strings that will be applied to
    the object to get the lookup args.
    """
    read_only = True
    def __init__(self, view_name=None, lookup_arg_attrs=None):
        self.view_name = view_name
        self.lookup_args = lookup_arg_attrs or ('project.slug', 'id')
        super(URLField, self).__init__()
    def _get_default_view_name(self, obj):
        return 'api:api-{}-detail'.format(obj.__class__._meta.verbose_name_plural[:])
    def _get_lookup_args(self, obj):
        return tuple(nested_getattr(obj, attr) for attr in self.lookup_args)
    def get_attribute(self, obj):
        return obj
    def to_representation(self, value):
        view = self.view_name or self._get_default_view_name(value)
        args = self._get_lookup_args(value)
        return reverse(view, args=args, request=self.context['request'])

class ProjectSlugField(ReadOnlyField):
    def __init__(self, *args, **kwargs):
        self.queryset = Project.objects.all()
        super(ProjectSlugField, self).__init__(*args, **kwargs)
    def get_attribute(self, obj):
        return obj.get_affiliation()
    def to_representation(self, value):
        url = reverse('api:api-project-detail', args=(value.slug,),
                      request=self.context['request'])
        return { 'name': value.name, 'url': url }

class HyperlinkedProjectItemField(HyperlinkedRelatedField):
    def get_attribute(self, obj):
        return get_attribute(obj, self.source_attrs)
    def to_representation(self, value):
        """
        Return URL from item requiring project slug kwarg
        """
        try:
            return reverse(
                self.view_name, args=[value.project.slug, value.id],
                request=self.context.get('request', None),
                format=self.format or self.context.get('format', None))
        except NoReverseMatch:
            raise Exception('Could not resolve URL for document.')

class UpdatersField(ReadOnlyField):
    read_only = True
    def get_attribute(self, obj):
        return obj.get_all_updaters()
    def to_representation(self, value):
        return [u.username for u in value]

class TopicAssignmentField(RelatedField):
    def __init__(self, *args, **kwargs):
        # FIXME always override?
        kwargs['queryset'] = TopicAssignment.objects.all()
        super(TopicAssignmentField, self).__init__(*args, **kwargs)
        self.many = True
    def _format_topic_assignment(self, ta):
        url = reverse('api:api-topics-detail',
                      args=(ta.topic.project.slug, ta.topic.id),
                      request=self.context['request'])
        return {
            'id': ta.topic.id,
            'preferred_name': ta.topic.preferred_name,
            'url': url
        }
    def get_attribute(self, obj):
        return obj.related_topics.all() if hasattr(obj, 'related_topics') else []
    def to_representation(self, value):
        return [self._format_topic_assignment(ta) for ta in value]
    def to_internal_value(self, data):
        if self.read_only:
            return
        # FIXME
        return []
    def field_from_native(self, data, files, field_name, into):
        if self.read_only:
            return
        into[field_name] = data.get(field_name, [])

class RelatedTopicSerializerMixin(object):
    def save_related_topics(self, obj, topics):
        """
        Given an array of names, make sure obj is related to those topics.
        """
        to_create = topics[:]
        to_delete = []

        for assignment in obj.related_topics.select_related('topic').all():
            topic_name = assignment.topic.preferred_name
            if topic_name in topics:
                to_create.remove(topic_name)
            else:
                to_delete.append(assignment)

        for assignment in to_delete:
            assignment.delete()

        user = self.context['request'].user
        project = self.context['request'].project

        for topic_name in to_create:
            topic = Topic.objects.get_or_create_by_name(
                topic_name, project, user)
            obj.related_topics.create(topic=topic, creator_id=user.id)
    def create(self, validated_data):
        topics = validated_data.pop('related_topics', None)
        obj = super(RelatedTopicSerializerMixin, self).create(validated_data)
        if topics is not None:
            self.save_related_topics(obj, topics)
        return obj
    def update(self, instance, validated_data):
        topics = validated_data.pop('related_topics', None)
        super(RelatedTopicSerializerMixin, self).update(instance, validated_data)
        if topics is not None:
            self.save_related_topics(instance, topics)
        return instance

    # FIXME
    def ___save_object(self, obj, **kwargs):
        # Need to change to allow partial updates, etc.
        topics = []
        if getattr(obj, '_m2m_data', None):
            topics = obj._m2m_data.pop('related_topics')
        super(RelatedTopicSerializerMixin, self).save_object(obj, **kwargs)
        self.save_related_topics(obj, topics)
