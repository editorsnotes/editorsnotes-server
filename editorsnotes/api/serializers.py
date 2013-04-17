from rest_framework import serializers
from rest_framework.relations import RelatedField
from editorsnotes.main import models as main_models

class TopicSerializer(serializers.ModelSerializer):
    topics = RelatedField('topics', many=True)
    creator = serializers.Field(source='creator.username')
    last_updater = serializers.Field(source='last_updater.username')
    class Meta:
        model = main_models.Topic
        fields = ('id', 'preferred_name', 'type', 'topics', 'summary',
                  'creator', 'last_updater')

class DocumentSerializer(serializers.ModelSerializer):
    topics = RelatedField('topics', many=True)
    class Meta:
        model = main_models.Document
        fields = ('id', 'description',)


######

class NoteSectionField(serializers.RelatedField):
    def to_native(self, value):
        if getattr(value, 'citationns'):
            serializer = CitationNSSerializer(value.citationns)
        elif getattr(value, 'textns'):
            serializer = TextNSSerializer(value.textns)
        elif getattr(value, 'notereferencens'):
            serializer = NoteReferenceNSSerializer(value.notereferencens)
        else:
            raise NotImplementedError('No such note section type')
        return serializer.data

class MinimalNoteSerializer(serializers.ModelSerializer):
    topics = RelatedField('topics', many=True)
    class Meta:
        model = main_models.Note
        fields = ('id', 'title', 'topics', 'content', 'status',)

class SectionOrderingField(serializers.WritableField):
    def section_ids(note):
        return [ns.note_section_id for ns in note.sections.all()]
    def field_to_native(self, obj, field_name):
        return section_ids(note)
    def field_from_native(self, data, files, field_name, into):
        note = self.root.object
        ids = data[field_name]

        if not isinstance(ids, list):
            raise serializers.ValidationError('Must be a list')

        different_ids = set.symmetric_difference(
            set(ids), set(section_ids(note)))

        if len(different_ids):
            raise serializers.ValidationError(
                'Must contain every section id and no more')

        for section in note.sections.all():
            section.ordering = data[field_name].index(section.note_section_id)
            section.save()

        # we don't need to update the "into" dict, because nothing changed.
        # The section_ordering list doesn't map to a native object.
        return

class TextNSSerializer(serializers.ModelSerializer):
    class Meta:
        model = main_models.notes.TextNS
        fields = ('id', 'content',)

class CitationNSSerializer(serializers.ModelSerializer):
    document = DocumentSerializer()
    document_id = serializers.WritableField(source='document_id')
    section_type = serializers.Field(source='section_type')
    class Meta:
        model = main_models.notes.CitationNS
        fields = ('id', 'section_type', 'document', 'content',)

class NoteReferenceNSSerializer(serializers.ModelSerializer):
    note_reference = MinimalNoteSerializer()
    note_reference_id = serializers.WritableField(source='note_reference_id')
    class Meta:
        model = main_models.notes.NoteReferenceNS
        fields = ('id', 'note_reference')


class NoteSerializer(serializers.ModelSerializer):
    topics = RelatedField('topics', many=True)
    section_ordering = SectionOrderingField()
    sections = NoteSectionField(many=True)
    class Meta:
        model = main_models.Note
        fields = ('id', 'title', 'topics', 'content', 'status', 
                  'section_ordering', 'sections',)
