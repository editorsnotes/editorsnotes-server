from collections import namedtuple

from django.core import urlresolvers

from rest_framework import mixins
from rest_framework import serializers
from rest_framework.reverse import reverse

from editorsnotes.auth.models import Project

from .. import serializers as en_serializers
from ..hydra import operation_from_perm
from ..ld import CONTEXT
from ..permissions import ProjectSpecificPermissions


def link_properties_for_project(project, request):
    project_hydra_class, = filter(
        lambda hydra_class: hydra_class['label'] == 'Project',
        ProjectHydraClassesSerializer(
            project, context={'request': request}
        ).data['hydra:supportedClass'])

    supported_properties = [
        prop['property'] for prop in
        project_hydra_class['hydra:supportedProperty']
    ]

    return [
        prop for prop in supported_properties
        if isinstance(prop, dict)
        and prop.get('label') in ('notes', 'topics', 'documents')
    ]


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

    # TODO: rdfs:subClassOf

    # This would be, i.e. "A Note is material created by a researcher."
    description = serializers.SerializerMethodField()

    label = serializers.SerializerMethodField()
    hydra_supportedOperation = serializers.SerializerMethodField()
    hydra_supportedProperty = serializers.SerializerMethodField()

    class Meta:
        model = Project

    def __init__(self, *args, **kwargs):
        self.class_serializer = kwargs.pop('class_serializer')
        self.vocab_base = kwargs.pop('vocab_base')
        super(HydraProjectClassSerializer, self).__init__(*args, **kwargs)

    def get_jsonld_id(self, obj):
        return '{}{}'.format(self.vocab_base, self.get_label(obj))

    def get_jsonld_type(self, obj):
        return 'hydra:Class'

    def get_label(self, obj):
        return self.class_serializer.__name__.replace('Serializer', '')

    def get_description(self, obj):
        return

    def get_hydra_supportedOperation(self, obj):
        url_field = self.class_serializer().get_fields().get('url')
        identity_serializer = HyperlinkedHydraPropertySerializer(
            url_field, self.get_label(obj).lower(),
            domain=self.vocab_base, parent_model=obj,
            context=self.context)
        return identity_serializer.data.get('hydra:supportedOperation')

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
                domain=self.vocab_base,
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
                obj, self.property_name,
                self.domain, self.parent_model,
                context=self.context
            ).data
        return self.context_dict.get(self.property_name)

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
            'label': label,
            'description': None,
            'hydra:method': 'GET',
            'hydra:expects': None,
            'hydra:returns': self.get_range(obj),
            'hydra:possibleStatus': []
        }

    def get_jsonld_id(self, obj):
        return '{}{}/{}'.format(
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
            (self.domain + self.get_label(obj).title())
        )

    def get_domain(self, obj):
        return '{}{}'.format(
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

                if 'hydra:expects' in operation:
                    operation['hydra:expects'] = \
                        self.domain + child_label.title()

                if 'hydra:returns' in operation:
                    operation['hydra:returns'] = \
                        self.domain + child_label.title()
                operations.append(operation)

        return operations

SUPPORTED_CLASS_SERIALIZERS = (
    en_serializers.ProjectSerializer,
    en_serializers.NoteSerializer,
    en_serializers.TopicSerializer,
    en_serializers.DocumentSerializer,
    # en_serializers.UserSerializer,
    # en_serializers.ActivitySerializer,
    # en_serializers.ScanSerializer,
    # en_serializers.TranscriptSerializer,
)


class ProjectHydraClassesSerializer(ReplaceLDFields,
                                    serializers.ModelSerializer):
    "Serializer to generate Hydra documentation for a project."
    jsonld_id = serializers.SerializerMethodField()
    jsonld_type = serializers.SerializerMethodField()
    hydra_supportedClass = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            'jsonld_id',
            'jsonld_type',
            'hydra_supportedClass',
        )

    def get_jsonld_id(self, obj):
        return reverse('api:projects-api-documentation', [obj.slug],
                       request=self.context['request'])

    def get_jsonld_type(self, obj):
        return 'hydra:ApiDocumentation'

    def get_hydra_supportedClass(self, obj):
        return [
            HydraProjectClassSerializer(
                obj, source='*', class_serializer=Serializer,
                vocab_base='{}#'.format(self.get_jsonld_id(obj)),
                context=self.context
            ).data
            for Serializer in SUPPORTED_CLASS_SERIALIZERS
        ]
