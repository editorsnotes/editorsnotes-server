from collections import namedtuple

from django.core import urlresolvers

from rest_framework import mixins
from rest_framework import serializers

from .. import serializers as en_serializers
from ..hydra import operation_from_perm
from ..ld import CONTEXT
from ..permissions import ProjectSpecificPermissions


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


PERM_ERROR = (
    'Can only generate permissions for a single ProjectSpecificPermission.')


def get_view_permission(view_obj, method):
    request = namedtuple('FakeRequest', 'method')(method)
    permissions = view_obj.get_permissions()

    assert len(permissions) == 1, PERM_ERROR
    assert isinstance(permissions[0], ProjectSpecificPermissions), PERM_ERROR

    permission, = permissions
    view_permissions = permission.get_view_permissions(request, view_obj)

    assert len(view_permissions) == 1, PERM_ERROR

    return view_permissions[0]

SUPPORTED_HYDRA_METHODS = {
    'GET': 'retrieve',
    'POST': 'create',
    'PUT': 'update',
    'DELETE': 'delete'
}


class ReplaceLDFields(object):
    """
    Mixin to rename fields with reserved characters.

      * jsonld_{FIELD} => @{FIELD}
      * hydra_{FIELD} => hydra:FIELD
    """
    def __init__(self, *args, **kwargs):
        super(ReplaceLDFields, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field.startswith('hydra_'):
                hydra_name = field.replace('hydra_', 'hydra:')
                self.fields[hydra_name] = self.fields.pop(field)
            if field.startswith('jsonld_'):
                jsonld_name = field.replace('jsonld_', '@')
                self.fields[jsonld_name] = self.fields.pop(field)


class HydraProjectClassSerializer(ReplaceLDFields, serializers.Serializer):
    """
    Serializer to generate a hydra:Class based on a project and ModelSerializer
    class.
    """
    jsonld_id = serializers.SerializerMethodField()
    jsonld_type = serializers.SerializerMethodField()

    label = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    hydra_supportedProperty = serializers.SerializerMethodField()

    class Meta:
        model = Project

    def __init__(self, *args, **kwargs):
        self.class_serializer = kwargs.pop('class_serializer')
        super(HydraProjectClassSerializer, self).__init__(*args, **kwargs)

    def get_jsonld_id(self, obj):
        return '{}:{}'.format(obj.slug, self.get_label(obj))

    def get_jsonld_type(self, obj):
        return 'hydra:Class'

    def get_label(self, obj):
        words = self.field_name.split('_')
        return ''.join(map(str.title, words))

    def get_description(self, obj):
        return

    def get_hydra_supportedProperty(self, obj):

        ignored_fields = [
            'id',
            'url',
            'type'
        ]

        return [
            HydraPropertySerializer(
                field, property_name,
                parent_model=obj,
                domain='wn',
                context=self.context
            ).data
            for property_name, field
            in self.class_serializer().get_fields().items()
            if property_name not in ignored_fields
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
                obj, self.property_name, self.domain, self.parent_model,
                context=self.context
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
        return '{}:{}/{}'.format(
            self.domain,
            self.parent_model._meta.verbose_name.title(),
            self.get_label(obj)
        )

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
        return '{}:{}'.format(
            self.domain,
            self.parent_model._meta.verbose_name.title()
        )

    def get_hydra_supportedOperation(self, obj):
        operations = []

        parent_label = self.parent_model._meta.verbose_name
        child_label = self.view_class.queryset.model._meta.verbose_name

        view_obj = self.view_class()
        request = self.context['request']

        for method, op in SUPPORTED_HYDRA_METHODS.items():
            if method not in view_obj.allowed_methods:
                continue

            # FIXME: Not always true for notes... but that's OK. Maybe include
            # whether private notes will be included/excluded in the
            # description.
            if method == 'GET':
                operations.append(self._get_retrieve_operation(obj))
                continue

            required_permission = get_view_permission(view_obj, method)

            operation = operation_from_perm(
                request.user, self.parent_model, required_permission)

            if operation:
                operation['@id'] = '_:{}_{}_{}'.format(
                    parent_label, child_label, op
                )
                operation['label'] = '{} a {} for this {}.'.format(
                    op.title(), child_label, parent_label)

                if 'expects' in operation:
                    operation['expects'] = \
                        self.domain + ':' + child_label.title()

                if 'returns' in operation:
                    operation['returns'] = \
                        self.domain + ':' + child_label.title()
                operations.append(operation)

        return operations


class ProjectHydraClassesSerializer(serializers.ModelSerializer):
    "Serializer to generate Hydra documentation for a project."
    project = HydraProjectClassSerializer(
        source='*',
        class_serializer=en_serializers.ProjectSerializer
    )

    # user = HydraProjectClassSerializer(
    #     source='*',
    #     class_serializer=en_serializers.NoteSerializer
    # )

    # activity = HydraClassSerializer(
    #     source='*',
    #     class_serializer=en_serializers.ActivitySerializer
    # )

    note = HydraProjectClassSerializer(
        source='*',
        class_serializer=en_serializers.NoteSerializer
    )

    # topic = HydraProjectClassSerializer(
    #     source='*',
    #     class_serializer=en_serializers.TopicSerializer
    # )

    # document = HydraProjectClassSerializer(
    #     source='*',
    #     class_serializer=en_serializers.DocumentSerializer
    # )

    # scan = HydraProjectClassSerializer(
    #     source='*',
    #     class_serializer=en_serializers.ScanSerializer
    # )

    # transcript = HydraProjectClassSerializer(
    #     source='*',
    #     class_serializer=en_serializers.TranscriptSerializer
    # )

    class Meta:
        model = Project
