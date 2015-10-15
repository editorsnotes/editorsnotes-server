from licensing.models import License
from rest_framework import serializers

from editorsnotes.main.models import Note
from editorsnotes.main.models.notes import NOTE_STATUS_CHOICES

from ..fields import (CurrentProjectDefault, HyperlinkedAffiliatedProjectField,
                      TopicAssignmentField, IdentityURLField, UpdatersField,
                      UnqualifiedURLField)
from ..validators import UniqueToProjectValidator

from .base import EmbeddedItemsMixin, RelatedTopicSerializerMixin


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
    url = IdentityURLField()
    project = HyperlinkedAffiliatedProjectField(
        default=CurrentProjectDefault())

    license = LicenseSerializer(read_only=True, source='get_license')
    updaters = UpdatersField()

    status = NoteStatusField()
    related_topics = TopicAssignmentField(many=True)

    references = UnqualifiedURLField(source='get_referenced_items')
    referenced_by = UnqualifiedURLField(source='get_referencing_items')

    class Meta:
        model = Note
        fields = (
            'id',
            'url',
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
            'related_topics'
            'references',
            'referenced_by',
        )
        validators = [
            UniqueToProjectValidator('title')
        ]

    def __init__(self, *args, **kwargs):
        minimal = kwargs.pop('minimal', False)
        super(NoteSerializer, self).__init__(*args, **kwargs)
        if minimal:
            self.fields.pop('_embedded', None)
            self.fields.pop('markup')
            self.fields.pop('markup_html')
