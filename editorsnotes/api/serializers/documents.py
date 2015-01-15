from collections import OrderedDict
import json

from lxml import etree
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueValidator

from editorsnotes.main.models import Document, Citation, Scan, Transcript
from editorsnotes.main.utils import remove_stray_brs

from .base import (RelatedTopicSerializerMixin, CurrentProjectDefault,
                   URLField, ProjectSlugField, HyperlinkedProjectItemField,
                   TopicAssignmentField)

class ZoteroField(serializers.Field):
    def to_representation(self, value):
        return value and json.loads(value, object_pairs_hook=OrderedDict)
    def to_internal_value(self, data):
        return json.dumps(data)

class HyperLinkedImageField(serializers.ImageField):
    def to_native(self, value):
        if not value.name:
            ret = None
        elif 'request' in self.context:
            ret = self.context['request'].build_absolute_uri(value.url)
        else:
            ret = value.url
        return ret

class ScanSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')
    image = HyperLinkedImageField()
    image_thumbnail = HyperLinkedImageField(read_only=True)
    class Meta:
        model = Scan
        fields = ('id', 'image', 'image_thumbnail', 'ordering', 'created',
                  'creator',)

class UniqueDocumentDescriptionValidator:
    message = u'Document with this description already exists.'
    def set_context(self, serializer):
        self.instance = getattr(self, 'instance', None)
    def __call__(self, attrs):
        if self.instance is not None:
            description = attrs.get('description', self.instance.description)
        else:
            description = attrs['description']

        project = attrs['project']
        qs = Document.objects.filter(
            description_digest=Document.hash_description(description),
            project=project)
        if self.instance is not None:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError({ 'description': [self.message] })

class DocumentSerializer(RelatedTopicSerializerMixin,
                         serializers.ModelSerializer):
    url = URLField()
    project = ProjectSlugField(default=CurrentProjectDefault())
    transcript = serializers.SerializerMethodField('get_transcript_url')
    zotero_data = ZoteroField(required=False)
    related_topics = TopicAssignmentField()
    scans = ScanSerializer(many=True, required=False, read_only=True)
    class Meta:
        model = Document
        fields = ('id', 'description', 'url', 'project', 'last_updated',
                  'scans', 'transcript', 'related_topics', 'zotero_data',)
        validators = [
            UniqueDocumentDescriptionValidator()
        ]
    def get_transcript_url(self, obj):
        if not obj.has_transcript():
            return None
        return reverse('api:api-transcripts-detail',
                       args=(obj.project.slug, obj.id),
                       request=self.context.get('request', None))
    def validate_description(self, value):
        description_stripped = Document.strip_description(value)
        if not description_stripped:
            raise serializer.ValidationError('Field required.')
        remove_stray_brs(value)
        return value


class TranscriptSerializer(serializers.ModelSerializer):
    url = URLField(lookup_arg_attrs=('document.project.slug', 'document.id'))
    document = HyperlinkedProjectItemField(view_name='api:api-documents-detail',
                                           queryset=Document.objects,
                                           required=True)
    class Meta:
        model = Transcript

class CitationSerializer(serializers.ModelSerializer):
    url = URLField('api:api-topic-citations-detail',
                   ('content_object.project.slug', 'content_object.topic_node_id', 'id'))
    document = HyperlinkedProjectItemField(view_name='api:api-documents-detail',
                                           queryset=Document.objects,
                                           required=True)
    document_description = serializers.SerializerMethodField('get_document_description')
    class Meta:
        model = Citation
        fields = ('id', 'url', 'ordering', 'document', 'document_description', 'notes')
    def get_document_description(self, obj):
        return etree.tostring(obj.document.description)
