from itertools import chain

from django.core.urlresolvers import resolve, NoReverseMatch, Resolver404
from rest_framework.relations import (HyperlinkedRelatedField, RelatedField,
                                      get_attribute)
from rest_framework.reverse import reverse
from rest_framework.serializers import (ReadOnlyField, ModelSerializer,
                                        SerializerMethodField)

from editorsnotes.auth.models import Project
from editorsnotes.main.models import Topic
from editorsnotes.main.utils import markup_html


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


class EmbeddedItemsURLField(ReadOnlyField):
    def to_representation(self, value):
        urls_by_type = markup_html.get_embedded_item_urls(value)
        embedded_urls = set(chain(*urls_by_type.values()))

        request = self.context.get('request')
        if request:
            embedded_urls = [
                request.build_absolute_uri(url) for url in embedded_urls
            ]

        return embedded_urls


class URLField(ReadOnlyField):
    """
    An identity URL field.

    lookup_kwarg_attrs should be a dictionary of strings whose values will be
    applied to the object to get the lookup args.
    """
    read_only = True

    def __init__(self, view_name=None, lookup_kwarg_attrs=None):
        self.view_name = view_name
        self.lookup_kwargs = lookup_kwarg_attrs or {
            'project_slug': 'project.slug',
            'pk': 'id'
        }
        super(URLField, self).__init__()

    def _get_default_view_name(self, obj):
        return 'api:{}-detail'.format(
            obj.__class__._meta.verbose_name_plural[:])

    def _get_lookup_kwargs(self, obj):
        return dict((k, nested_getattr(obj, v))
                    for k, v in self.lookup_kwargs.items())

    def get_attribute(self, obj):
        return obj

    def to_representation(self, value):
        view = self.view_name or self._get_default_view_name(value)
        kwargs = self._get_lookup_kwargs(value)
        return reverse(view, kwargs=kwargs, request=self.context['request'])


class ProjectSlugField(ReadOnlyField):
    def __init__(self, *args, **kwargs):
        self.queryset = Project.objects.all()
        super(ProjectSlugField, self).__init__(*args, **kwargs)

    def get_attribute(self, obj):
        return obj.get_affiliation()

    def to_representation(self, value):
        url = reverse('api:projects-detail',
                      request=self.context['request'],
                      kwargs={
                          'project_slug': value.slug
                      })
        return {'name': value.name, 'url': url}


class HyperlinkedProjectItemField(HyperlinkedRelatedField):
    def get_attribute(self, obj):
        return get_attribute(obj, self.source_attrs)

    def to_representation(self, value):
        """
        Return URL from item requiring project slug kwarg
        """
        try:
            return reverse(
                self.view_name, kwargs={'project_slug': value.project.slug,
                                        'pk': value.id},
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


class MinimalTopicSerializer(ModelSerializer):
    url = URLField(lookup_kwarg_attrs={
        'project_slug': 'project.slug',
        'topic_node_id': 'topic_node_id'
    })
    topic_node_id = SerializerMethodField()

    class Meta:
        model = Topic
        fields = ('id', 'topic_node_id', 'preferred_name', 'url',)

    def get_topic_node_id(self, obj):
        return obj.topic_node_id


class TopicAssignmentField(RelatedField):
    default_error_messages = {
        'no_match': 'No topic matches this URL.',
        'outside_project': 'Related topics must be within the same project.',
        'bad_path': 'This URL is not a topic API url.'
    }

    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = Topic.objects.all()
        super(TopicAssignmentField, self).__init__(*args, **kwargs)

    def get_attribute(self, obj):
        return [ta.topic for ta in obj.related_topics.all()]

    def to_representation(self, topics):
        return [MinimalTopicSerializer(topic, context=self.context).data
                for topic in topics]

    def to_internal_value(self, data):
        if self.read_only:
            return
        return [self._topic_from_url(url) for url in data]

    def _topic_from_url(self, url):
        try:
            match = resolve(url)
        except Resolver404:
            self.fail('no_match')

        if match.view_name != 'api:topics-detail':
            self.fail('bad_path')

        current_project = self.context['request'].project
        lookup_project_slug = match.kwargs.pop('project_slug')
        if lookup_project_slug != current_project.slug:
            self.fail('outside_project')

        return self.get_queryset().get(project=current_project, **match.kwargs)


class RelatedTopicSerializerMixin(object):
    def save_related_topics(self, obj, topics):
        """
        Given an array of names, make sure obj is related to those topics.
        """
        rel_topics = obj.related_topics.select_related('topic').all()

        new_topics = set(topics)
        existing_topics = {ta.topic for ta in rel_topics}

        to_create = new_topics.difference(existing_topics)
        to_delete = existing_topics.difference(new_topics)

        # Delete unused topic assignments
        rel_topics.filter(topic__in=to_delete).delete()

        # Create new topic assignments
        for topic in to_create:
            obj.related_topics.create(
                topic=topic, creator_id=self.context['request'].user.id)

    def create(self, validated_data):
        topics = validated_data.pop('related_topics', None)
        obj = super(RelatedTopicSerializerMixin, self).create(validated_data)
        if topics is not None:
            self.save_related_topics(obj, topics)
        return obj

    def update(self, instance, validated_data):
        topics = validated_data.pop('related_topics', None)
        super(RelatedTopicSerializerMixin, self)\
            .update(instance, validated_data)
        if topics is not None:
            self.save_related_topics(instance, topics)
        return instance
