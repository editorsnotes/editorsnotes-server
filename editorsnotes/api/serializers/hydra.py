from rest_framework import serializers

from .. import serializers as en_serializers
from ..ld import CONTEXT


class HydraPropertySerializer(serializers.Serializer):
    property = serializers.SerializerMethodField()
    hydra_title = serializers.SerializerMethodField()
    hydra_description = serializers.ReadOnlyField(source='help_text')
    hydra_required = serializers.ReadOnlyField(source='required')
    hydra_writeonly = serializers.ReadOnlyField(source='write_only')
    hydra_readonly = serializers.ReadOnlyField(source='read_only')

    def __init__(self, instance, property_name, **kwargs):
        self.property_name = property_name
        self.context_dict = kwargs.pop('context_dict', CONTEXT)

        super(HydraPropertySerializer, self).__init__(instance, **kwargs)

        for field in self.fields:
            if field.startswith('hydra_'):
                coloned_name = field.replace('hydra_', 'hydra:')
                self.fields[coloned_name] = self.fields.pop(field)

    def get_property(self, obj):
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
            HydraPropertySerializer(field, property_name)
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
