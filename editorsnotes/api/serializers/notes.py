from licensing.models import License
from rest_framework import serializers

from editorsnotes.main.models import Note
from editorsnotes.main.models.notes import NOTE_STATUS_CHOICES

from .base import (RelatedTopicSerializerMixin, CurrentProjectDefault,
                   URLField, ProjectSlugField, TopicAssignmentField,
                   EmbeddedMarkupReferencesMixin)

from .auth import MinimalUserSerializer
from ..validators import UniqueToProjectValidator


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
class NoteSerializer(RelatedTopicSerializerMixin,
                     EmbeddedMarkupReferencesMixin,
                     serializers.ModelSerializer):
    url = URLField()
    project = ProjectSlugField(default=CurrentProjectDefault())
    license = LicenseSerializer(read_only=True, source='get_license')
    updaters = MinimalUserSerializer(read_only=True, many=True,
                                     source='get_all_updaters')
    status = NoteStatusField()
    related_topics = TopicAssignmentField()

    class Meta:
        model = Note
        fields = ('id', 'title', 'url', 'project', 'license',
                  'is_private', 'last_updated', 'updaters', 'related_topics',
                  'markup', 'markup_html', 'status',)
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
