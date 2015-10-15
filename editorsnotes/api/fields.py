from itertools import chain

from django.core.urlresolvers import resolve, NoReverseMatch, Resolver404
from rest_framework.relations import (
    HyperlinkedRelatedField, RelatedField, get_attribute)
from rest_framework.reverse import reverse
from rest_framework.serializers import (
    ModelSerializer, ReadOnlyField, SerializerMethodField)

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


class HyperlinkedAffiliatedProjectField(ReadOnlyField):
    def get_attribute(self, obj):
        return obj.get_affiliation()
    def to_representation(self, value):
        request = self.context['request']
        return request.build_absolute_uri(value.get_absolute_url())


class UnqualifiedURLField(ReadOnlyField):
    def get_attribute(self, obj):
        # FIXME: format too
        request = self.context['request']
        value = super(ReadOnlyField, self).get_attribute(obj)

        make_url = lambda path: request.build_absolute_uri(path)

        return (
            make_url(value) if isinstance(value, basestring)
            else map(make_url, value)
        )


class IdentityURLField(ReadOnlyField):
    """
    URL field that will use an object's get_absolute_url function to create a
    fully qualified URL.
    """
    def get_attribute(self, obj):
        return obj.get_absolute_url()

    def to_representation(self, value):
        return self.context['request'].build_absolute_uri(value)


class CustomLookupHyperlinkedField(HyperlinkedRelatedField):
    """
    HyperlinkedRelatedField that allows custom URL lookup definitions

    lookup_kwarg_attrs should be a dictionary of strings whose values will be
    applied to the object to get the lookup args.

    If no view_name is provided, it will be inferred from the object itself.
    """
    read_only = True

    def __init__(self, view_name=None, lookup_kwarg_attrs=None,
                 *args, **kwargs):
        DEFAULT_LOOKUP_ATTRS = {
            'project_slug': 'project.slug',
            'pk': 'id'
        }
        self.lookup_kwargs = lookup_kwarg_attrs or DEFAULT_LOOKUP_ATTRS.copy()

        # View name will be figured out later, once the instance is known.
        self.view_name = None

        super(HyperlinkedRelatedField, self).__init__(*args, **kwargs)

    def get_default_view_name(self, obj):
        class_name = obj.__class__._meta.verbose_name_plural[:]
        return 'api:{}-detail'.format(class_name)

    def get_lookup_kwargs(self, obj):
        return dict(
            (key, nested_getattr(obj, val))
            for key, val in self.lookup_kwargs.items())

    def get_attribute(self, instance):
        return instance

    def get_url(self, obj, view_name, request, format):
        view_name = self.view_name or self.get_default_view_name(obj)
        url_kwargs = self.get_lookup_kwargs(obj)

        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class UpdatersField(ReadOnlyField):
    read_only = True

    def get_attribute(self, obj):
        return obj.get_all_updaters()

    def to_representation(self, value):
        return [u.username for u in value]


class MinimalTopicSerializer(ModelSerializer):
    url = IdentityURLField()

    class Meta:
        model = Topic
        fields = ('id', 'preferred_name', 'url',)


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
