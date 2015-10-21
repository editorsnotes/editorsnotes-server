from licensing.models import License
from rest_framework import serializers

from editorsnotes.main.models import Note
from editorsnotes.main.models.notes import NOTE_STATUS_CHOICES

from .. import fields
from ..ld import ROOT_NAMESPACE
from ..validators import UniqueToProjectValidator

from .mixins import EmbeddedItemsMixin, RelatedTopicSerializerMixin


__all__ = ['NoteSerializer']


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = ('url', 'name', 'symbols',)


class NoteStatusField(serializers.ReadOnlyField):
    def get_attribute(self, obj):
        return obj.get_status_display().lower() if obj else 'open'

    def to_internal_value(self, data):
        status_choice = [val for val, label in NOTE_STATUS_CHOICES
                         if label.lower() == data.lower()]
        if not len(status_choice):
            raise serializers.ValidationError('Invalid status. Choose between '
                                              'open, closed, or hibernating.')
        return status_choice[0]


# TODO: change license, fuller repr of updaters
class NoteSerializer(RelatedTopicSerializerMixin, EmbeddedItemsMixin,
                     serializers.ModelSerializer):
    url = fields.IdentityURLField(view_name='api:notes-detail')
    type = serializers.SerializerMethodField()
    project = fields.HyperlinkedAffiliatedProjectField(
        default=fields.CurrentProjectDefault())

    license = LicenseSerializer(read_only=True, source='get_license')
    updaters = fields.UpdatersField()

    status = NoteStatusField()
    related_topics = fields.TopicAssignmentField(many=True)

    references = fields.UnqualifiedURLField(
        source='get_referenced_items')
    referenced_by = fields.UnqualifiedURLField(
        source='get_referencing_items')

    class Meta:
        model = Note
        fields = (
            'id',
            'url',
            'type',
            'project',

            'title',

            'status',
            'is_private',
            'license',
            'created',
            'last_updated',
            'updaters',

            'markup',
            'markup_html',

            'related_topics',
            'references',
            'referenced_by',
        )
        embedded_fields = (
            'project',
            'updaters',
            'related_topics',
            'references',
            'referenced_by',
        )
        validators = [
            UniqueToProjectValidator('title')
        ]

    def get_type(self, obj):
        return ROOT_NAMESPACE + 'Note'
