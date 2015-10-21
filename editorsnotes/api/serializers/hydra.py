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


def view_permissions(view_obj, method):
    request = namedtuple('FakeRequest', 'method')(method)

    return [
        permission.get_view_permissions(request, view_obj)
        for permission in view_obj.get_permissions()
    ]

SUPPORTED_HYDRA_METHODS = ['GET', 'POST', 'PUT', 'DELETE']


class ReplaceLDFields(object):
    def __init__(self, *args, **kwargs):
        super(ReplaceLDFields, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field.startswith('hydra_'):
                hydra_name = field.replace('hydra_', 'hydra:')
                self.fields[hydra_name] = self.fields.pop(field)
            if field.startswith('jsonld_'):
                jsonld_name = field.replace('jsonld_', '@')
                self.fields[jsonld_name] = self.fields.pop(field)


class HydraClassSerializer(ReplaceLDFields, serializers.Serializer):
    "Serializer to generate a hydra:Class based on a serializer."
    jsonld_id = serializers.SerializerMethodField()
    jsonld_type = serializers.SerializerMethodField()

    label = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    supportedProperty = serializers.SerializerMethodField()

    def get_jsonld_id(self, obj):
        project = self.root.project  # ?
        return '{}:{}'.format(project.slug, self.get_label())

    def get_jsonld_type(self, obj):
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


class HydraPropertySerializer(ReplaceLDFields, serializers.Serializer):
    """
    Serializer to generate a hydra:supportedProperty based on a serializer
    field.
    """
    property = serializers.SerializerMethodField()
    hydra_title = serializers.SerializerMethodField()
    hydra_description = serializers.ReadOnlyField(source='help_text')
    hydra_required = serializers.ReadOnlyField(source='required')
    hydra_writeonly = serializers.ReadOnlyField(source='write_only')
    hydra_readonly = serializers.ReadOnlyField(source='read_only')

    def __init__(self, instance, property_name, domain=None, parent_model=None,
                 **kwargs):
        self.property_name = property_name
        self.domain = domain
        self.parent_model = parent_model
        self.context_dict = kwargs.pop('context_dict', CONTEXT)
        super(HydraPropertySerializer, self).__init__(instance, **kwargs)

    def get_property(self, obj):
        if isinstance(obj, serializers.HyperlinkedRelatedField):
            return HyperlinkedHydraPropertySerializer(
                obj, self.property_name, self.domain, self.parent_model
            ).data
        return self.context_dict[self.property_name]

    def get_hydra_title(self, obj):
        return self.property_name


class HyperlinkedHydraPropertySerializer(ReplaceLDFields,
                                         serializers.Serializer):
    """
    Serializer to generate a hydra:property based on a field that is an
    instance of DRF's HyperlinkedRelatedField.
    """
    jsonld_id = serializers.SerializerMethodField()
    jsonld_type = serializers.SerializerMethodField()

    label = serializers.SerializerMethodField()
    hydra_description = serializers.ReadOnlyField(source='help_text')

    domain = serializers.SerializerMethodField()
    range = serializers.SerializerMethodField()

    hydra_supportedOperation = serializers.SerializerMethodField()

    def __init__(self, instance, property_name, domain=None, parent_model=None,
                 **kwargs):
        self.property_name = property_name
        self.domain = domain
        self.parent_model = parent_model

        self.view_class = self._get_view_class(instance)
        super(HyperlinkedHydraPropertySerializer, self)\
            .__init__(instance, **kwargs)

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

    @property
    def is_collection(self):
        return issubclass(self.view_class, mixins.ListModelMixin)

    @property
    def model(self):
        return self.view_class.queryset.model

    def _get_retrieve_operation(self, obj):
        parent_label = self.parent_model._meta.verbose_name
        label = self.get_label(obj)

        jsonld_id = '_:{}_{}_retrieve'.format(parent_label, label)

        label = 'Retrieve {} for this {}.'.format(
            ('all ' if self.is_collection else '') + label,
            parent_label
        )

        return {
            '@id': jsonld_id,
            '@type': 'hydra:Operation',
            'hydra:method': 'GET',
            'label': label,
            'description': None,
            'expects': None,
            'returns': self.get_range(obj),
            'statusCodes': []
        }

    def get_jsonld_id(self, obj):
        return self.domain + '/' + self.get_label(obj)

    def get_jsonld_type(self, obj):
        return 'hydra:Link'

    def get_label(self, obj):
        return self.property_name

    def get_range(self, obj):
        return (
            'hydra:Collection' if self.is_collection else
            (self.domain + '/' + self.get_label(obj).title())
        )

    def get_domain(self, obj):
        return self.domain

    def get_hydra_supportedOperation(self, obj):
        operations = []

        view_obj = self.view_class()

        for method in SUPPORTED_HYDRA_METHODS:
            if method not in view_obj.allowed_methods:
                continue
            if method == 'GET':
                operations.append(self._get_retrieve_operation(obj))
                continue

            required_permissions = view_permissions(view_obj, method)

        return operations


class ProjectHydraClassesSerializer(serializers.Serializer):
    "Serializer to generate Hydra documentation for a project."
    project = HydraClassSerializer(en_serializers.ProjectSerializer)

    user = HydraClassSerializer(en_serializers.NoteSerializer)
    activity = HydraClassSerializer(en_serializers.ActivitySerializer)

    note = HydraClassSerializer(en_serializers.NoteSerializer)
    topic = HydraClassSerializer(en_serializers.TopicSerializer)

    document = HydraClassSerializer(en_serializers.DocumentSerializer)
    scan = HydraClassSerializer(en_serializers.ScanSerializer)
    transcript = HydraClassSerializer(en_serializers.TranscriptSerializer)
