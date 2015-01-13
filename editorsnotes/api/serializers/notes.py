from lxml import etree

from rest_framework import serializers

from editorsnotes.main.models import (Note, TextNS, CitationNS, NoteReferenceNS,
                                      Document)
from editorsnotes.main.models.notes import NOTE_STATUS_CHOICES

from .base import (RelatedTopicSerializerMixin, CurrentProjectDefault,
                   URLField, ProjectSlugField, UpdatersField,
                   HyperlinkedProjectItemField, TopicAssignmentField)


class TextNSSerializer(serializers.ModelSerializer):
    section_id = serializers.ReadOnlyField(source='note_section_id')
    section_type = serializers.ReadOnlyField(source='section_type_label')
    class Meta:
        model = TextNS
        fields = ('section_id', 'section_type', 'ordering', 'content',)

class CitationNSSerializer(serializers.ModelSerializer):
    section_id = serializers.ReadOnlyField(source='note_section_id')
    #note_id = serializers.ReadOnlyField(source='note_id')
    section_type = serializers.ReadOnlyField(source='section_type_label')
    document = HyperlinkedProjectItemField(view_name='api:api-documents-detail',
                                           queryset=Document.objects.all())
    document_description = serializers.SerializerMethodField()
    class Meta:
        model = CitationNS
        fields = ('section_id', 'section_type', 'ordering',
                  'document', 'document_description', 'content',)
    def get_document_description(self, obj):
        return etree.tostring(obj.document.description)

class NoteReferenceNSSerializer(serializers.ModelSerializer):
    section_id = serializers.ReadOnlyField(source='note_section_id')
    section_type = serializers.ReadOnlyField(source='section_type_label')
    note_reference = HyperlinkedProjectItemField(view_name='api:api-notes-detail',
                                                 queryset=Note.objects.all())
    note_reference_title = serializers.SerializerMethodField()
    class Meta:
        model = NoteReferenceNS
        fields = ('section_id', 'section_type', 'ordering',
                  'note_reference', 'note_reference_title', 'content',)
    def get_note_reference_title(self, obj):
        return obj.note_reference.title

def _serializer_from_section_type(section_type):
    if section_type == 'citation':
        serializer = CitationNSSerializer
    elif section_type == 'text':
        serializer = TextNSSerializer
    elif section_type == 'note_reference':
        serializer = NoteReferenceNSSerializer
    else:
        raise NotImplementedError(
            'No such note section type: {}'.format(section_type))
    return serializer

class NoteSectionField(serializers.RelatedField):
    def field_to_native(self, note, field_name):
        qs = note.sections.all().select_subclasses()\
                .select_related('citationns__document__project',
                                'notereferencens__note__project')
        return [self.to_native(section) for section in qs.all()]
    def to_native(self, section):
        serializer_class = _serializer_from_section_type(
            section.section_type_label)
        serializer = serializer_class(section, context=self.context)
        return serializer.data

class NoteStatusField(serializers.WritableField):
    def field_to_native(self, obj, field_name):
        return obj.get_status_display().lower() if obj else 'open'
    def from_native(self, data):
        status_choice = [ val for val, label in NOTE_STATUS_CHOICES
                          if label.lower() == data.lower() ]
        if not len(status_choice):
            raise serializers.ValidationError('Invalid status. Choose between '
                                              'open, closed, or hibernating.')
        return status_choice[0]

class NoteSerializer(RelatedTopicSerializerMixin,
                     serializers.ModelSerializer):
    url = URLField()
    project = ProjectSlugField(default=CurrentProjectDefault())
    updaters = UpdatersField()
    status = NoteStatusField()
    related_topics = TopicAssignmentField()
    sections = NoteSectionField(many=True)
    class Meta:
        model = Note
        fields = ('id', 'title', 'url', 'project', 'is_private', 'last_updated',
                  'updaters', 'related_topics', 'content', 'status', 'sections',)

class MinimalNoteSerializer(RelatedTopicSerializerMixin,
                            serializers.ModelSerializer):
    status = NoteStatusField()
    url = URLField()
    project = ProjectSlugField(default=CurrentProjectDefault())
    related_topics = TopicAssignmentField()
    class Meta:
        model = Note
        fields = ('id', 'url', 'title', 'related_topics', 'content', 'status',
                  'is_private',)
