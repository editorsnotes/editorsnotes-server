from django.core.urlresolvers import NoReverseMatch
from rest_framework.relations import HyperlinkedRelatedField, RelatedField
from rest_framework.reverse import reverse
from rest_framework.serializers import Field

from editorsnotes.main.models import Topic, TopicAssignment

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

class URLField(Field):
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
    def field_to_native(self, obj, field):
        view = self.view_name or self._get_default_view_name(obj)
        args = self._get_lookup_args(obj)
        return reverse(view, args=args, request=self.context['request'])

class ProjectSlugField(Field):
    read_only = True
    def field_to_native(self, obj, field_name):
        project = obj.get_affiliation()
        url = reverse('api:api-project-detail', args=(project.slug,),
                      request=self.context['request'])
        return { 'name': project.name, 'url': url }

class HyperlinkedProjectItemField(HyperlinkedRelatedField):
    def to_native(self, obj):
        """
        Return URL from item requiring project slug kwarg
        """
        try:
            return reverse(
                self.view_name, args=[obj.project.slug, obj.id],
                request=self.context.get('request', None),
                format=self.format or self.context.get('format', None))
        except NoReverseMatch:
            raise Exception('Could not resolve URL for document.')

class UpdatersField(Field):
    read_only = True
    def field_to_native(self, obj, field_name):
        return [u.username for u in obj.get_all_updaters()]

class TopicAssignmentField(RelatedField):
    def __init__(self, *args, **kwargs):
        super(TopicAssignmentField, self).__init__(*args, **kwargs)
        self.many = True
    def format_topic_assignment(self, ta):
        url = reverse('api:api-topics-detail',
                      args=(ta.topic.project.slug, ta.topic.id),
                      request=self.context['request'])
        return {
            'id': ta.topic.id,
            'preferred_name': ta.topic.preferred_name,
            'url': url
        }
    def field_to_native(self, obj, field_name):
        if obj is None:
            ret = []
        else:
            ret = [self.format_topic_assignment(ta) for ta in obj.related_topics.all()]
        return ret
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

    def save_object(self, obj, **kwargs):
        # Need to change to allow partial updates, etc.
        topics = []
        if getattr(obj, '_m2m_data', None):
            topics = obj._m2m_data.pop('related_topics')
        super(RelatedTopicSerializerMixin, self).save_object(obj, **kwargs)
        self.save_related_topics(obj, topics)
