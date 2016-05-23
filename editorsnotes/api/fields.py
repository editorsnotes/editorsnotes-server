from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.reverse import reverse
from rest_framework.serializers import ReadOnlyField

from editorsnotes.main.models import Topic


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
        return '%s()' % self.__class__.__name__


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
            make_url(value) if isinstance(value, str)
            else list(map(make_url, value))
        )


class CustomLookupHyperlinkedField(HyperlinkedRelatedField):
    """
    HyperlinkedRelatedField that allows custom URL lookup definitions

    lookup_kwarg_attrs should be a dictionary of strings whose values will be
    applied to the object to get the lookup args.

    If no view_name is provided, it will be inferred from the object itself.
    """
    read_only = True

    def __init__(self, *args, **kwargs):
        self.lookup_kwarg_attrs = kwargs.pop('lookup_kwarg_attrs')
        self.view_name = kwargs.pop('view_name')
        super(HyperlinkedRelatedField, self).__init__(*args, **kwargs)

    def get_lookup_kwargs(self, obj):
        return dict(
            (key, nested_getattr(obj, val))
            for key, val in list(self.lookup_kwarg_attrs.items()))

    def get_attribute(self, instance):
        return instance

    def get_url(self, obj, view_name, request, format):
        url_kwargs = self.get_lookup_kwargs(obj)
        return reverse(self.view_name, kwargs=url_kwargs,
                       request=request, format=format)


class IdentityURLField(CustomLookupHyperlinkedField):
    """
    CustomLookupHyperlinkedField meant to be used as an identity field.

    Provides a default that will be appropriate for notes, topics, and
    documents.
    """
    def __init__(self, *args, **kwargs):
        if 'lookup_kwarg_attrs' not in kwargs:
            kwargs['lookup_kwarg_attrs'] = {
                'project_slug': 'project.slug',
                'pk': 'id'
            }
        kwargs['read_only'] = True
        self.format = None
        super(IdentityURLField, self).__init__(*args, **kwargs)


class UpdatersField(ReadOnlyField):
    read_only = True

    def get_attribute(self, obj):
        return obj.get_all_updaters()

    def to_representation(self, value):
        request = self.context['request']
        return [
            request.build_absolute_uri(user.get_absolute_url())
            for user in value
        ]


class TopicAssignmentField(HyperlinkedRelatedField):
    default_error_messages = {
        'outside_project': 'Related topics must be within the same project.',
    }

    def __init__(self, *args, **kwargs):
        # Set these automatically
        kwargs['queryset'] = Topic.objects.all()
        kwargs['view_name'] = 'api:topics-detail'
        super(TopicAssignmentField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        args = (obj.topic.project.slug, obj.topic.id)
        return reverse('api:topics-detail', args=args, request=request,
                       format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        request = self.context['request']

        if view_kwargs['project_slug'] != request.project.slug:
            self.fail('outside_project')

        lookup_kwargs = {
            'project__slug': view_kwargs['project_slug'],
            'id': view_kwargs['pk']
        }

        return self.get_queryset().get(**lookup_kwargs)
