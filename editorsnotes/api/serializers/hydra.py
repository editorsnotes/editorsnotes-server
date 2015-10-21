from collections import namedtuple

from django.core import urlresolvers

from rest_framework import mixins
from rest_framework import serializers

from .. import serializers as en_serializers
from ..hydra import operation_from_perm
from ..ld import CONTEXT


def url_pattern_for_name(patterns, view_name):
    found = None

    for pattern in patterns:
        if isinstance(pattern, urlresolvers.RegexURLResolver):
            found = url_pattern_for_name(pattern.url_patterns, view_name)
        elif pattern.name == view_name:
            found = pattern

        if found:
            break

    return found


SUPPORTED_HYDRA_METHODS = ['GET', 'POST', 'PUT', 'DELETE']


class HyperlinkedHydraPropertySerializer(serializers.Serializer):
    jsonld_id = serializers.SerializerMethodField()
    jsonld_type = serializers.SerializerMethodField()

    label = serializers.SerializerMethodField()
    hydra_description = serializers.ReadOnlyField(source='help_text')

    domain = serializers.SerializerMethodField()
    range = serializers.SerializerMethodField()

    hydra_supportedOperation = serializers.SerializerMethodField()

    def __init__(self, instance, property_name, domain=None, **kwargs):
        self.domain = domain
        self.property_name = property_name

        self.view_class = self._get_view_class(instance)

        super(HyperlinkedHydraPropertySerializer, self)\
            .__init__(instance, **kwargs)

        for field in self.fields:
            if field.startswith('hydra_'):
                hydra_name = field.replace('hydra_', 'hydra:')
                self.fields[hydra_name] = self.fields.pop(field)
            if field.startswith('jsonld_'):
                jsonld_name = field.replace('jsonld_', '@')
                self.fields[jsonld_name] = self.fields.pop(field)

    def _get_view_class(self, obj):
        view_name = obj.view_name

        assert view_name.startswith('api:'), (
            'Can only make a hyperlinked Hydra property for hyperlinked '
            'fields whose view_names are in the `api` namespace (i.e. '
            'api:notes-detail).')

        _, view_name = view_name.split(':')
        _, api_resolver = urlresolvers.get_resolver(None).namespace_dict['api']

        pattern = url_pattern_for_name(api_resolver.url_patterns, view_name)

        if pattern is None:
            raise ValueError(
                'Could not find a URL pattern with name {}'.format(view_name))

        return pattern.callback.cls

    def _is_collection_view(self):
        return issubclass(self.view_class, mixins.ListModelMixin)

    def get_jsonld_id(self, obj):
        return self.domain + '/' + self.get_label(obj)

    def get_jsonld_type(self, obj):
        return 'hydra:Link'

    def get_label(self, obj):
        return self.property_name

    def get_range(self, obj):
        return (
            'hydra:Collection' if self._is_collection_view() else
            (self.domain + '/' + self.get_label(obj).title())
        )


    def get_domain(self, obj):
        return self.domain

    def _get_retrieve_operation(self, obj):
        return {
            '@id': '_:project_notes_retrieve',
            '@type': 'hydra:Operation',
            'hydra:method': 'GET',
            'label': 'Retrieve all notes for this project.',
            'description': None,
            'expects': None,
            'returns': self.get_range(obj),
            'statusCodes': []
        }

    def get_hydra_supportedOperation(self, obj):
        operations = []

        view_obj = self.view_class()

        for method in SUPPORTED_HYDRA_METHODS:
            if method not in view_obj.allowed_methods:
                continue
            if method == 'GET':
                operations.append(self._get_retrieve_operation(obj))
                continue

            required_permissions, = [
                permission.get_view_permissions(
                    namedtuple('FakeRequest', 'method')(method),
                    view_obj)
                for permission in view_obj.get_permissions()
            ]

        return operations



class HydraPropertySerializer(serializers.Serializer):
    property = serializers.SerializerMethodField()
    hydra_title = serializers.SerializerMethodField()
    hydra_description = serializers.ReadOnlyField(source='help_text')
    hydra_required = serializers.ReadOnlyField(source='required')
    hydra_writeonly = serializers.ReadOnlyField(source='write_only')
    hydra_readonly = serializers.ReadOnlyField(source='read_only')

    def __init__(self, instance, property_name, domain=None, **kwargs):
        self.domain = domain
        self.property_name = property_name
        self.context_dict = kwargs.pop('context_dict', CONTEXT)

        super(HydraPropertySerializer, self).__init__(instance, **kwargs)

        for field in self.fields:
            if field.startswith('hydra_'):
                hydra_name = field.replace('hydra_', 'hydra:')
                self.fields[hydra_name] = self.fields.pop(field)

    def get_property(self, obj):
        if isinstance(obj, serializers.HyperlinkedRelatedField):
            return HyperlinkedHydraPropertySerializer(
                obj, self.property_name, self.domain
            ).data
        return self.context_dict[self.property_name]

    def get_hydra_title(self, obj):
        return self.property_name


class HydraClassSerializer(serializers.Serializer):
    ld_id = serializers.SerializerMethodField()
    ld_type = serializers.SerializerMethodField()

    label = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    supportedProperty = serializers.SerializerMethodField()

    def get_ld_id(self, obj):
        project = self.root.project  # ?
        return '{}:{}'.format(project.slug, self.get_label())

    def get_ld_type(self, obj):
        return 'hydra:Class'

    def get_label(self, obj):
        words = self.field_name.split('_')
        return ''.join(map(str.title, words))

    def get_description(self, obj):
        return

    def get_supported_property(self):
        return [
            HydraPropertySerializer(field, property_name, context=self.context)
            for property_name, field in self.get_fields().items()
        ]


# common_hyperlinks = ...
class ProjectHydraClassesSerializer(serializers.Serializer):
    project = HydraClassSerializer(en_serializers.ProjectSerializer)

    user = HydraClassSerializer(en_serializers.NoteSerializer)
    activity = HydraClassSerializer(en_serializers.ActivitySerializer)

    note = HydraClassSerializer(en_serializers.NoteSerializer)
    topic = HydraClassSerializer(en_serializers.TopicSerializer)

    document = HydraClassSerializer(en_serializers.DocumentSerializer)
    scan = HydraClassSerializer(en_serializers.ScanSerializer)
    transcript = HydraClassSerializer(en_serializers.TranscriptSerializer)
