from collections import OrderedDict
import json

from lxml import etree
from rest_framework import serializers
from rest_framework.reverse import reverse

from editorsnotes.main.models import Document, Citation, Scan, Transcript

from .base import (RelatedTopicSerializerMixin, CurrentProjectDefault,
                   URLField, ProjectSlugField, HyperlinkedProjectItemField,
                   TopicAssignmentField)

class ZoteroField(serializers.WritableField):
    def to_native(self, zotero_data):
        return zotero_data and json.loads(zotero_data,
                                          object_pairs_hook=OrderedDict)
    def from_native(self, data):
        return data and json.dumps(data)

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

class DocumentSerializer(RelatedTopicSerializerMixin,
                         serializers.ModelSerializer):
    url = URLField()
    project = ProjectSlugField(default=CurrentProjectDefault())
    transcript = serializers.SerializerMethodField('get_transcript_url')
    zotero_data = ZoteroField(required=False)
    related_topics = TopicAssignmentField()
    scans = ScanSerializer(many=True, required=False, read_only=True)
    def get_validation_exclusions(self):
        # TODO: This can be removed in future versions of django rest framework.
        # It's necessary because for the time being, DRF excludes non-required
        # fields from validation (not something I find particularly useful, but
        # they must've had their reasons...)
        exclusions = super(DocumentSerializer, self).get_validation_exclusions()
        exclusions.remove('zotero_data')
        return exclusions
    def get_transcript_url(self, obj):
        if not obj.has_transcript():
            return None
        return reverse('api:api-transcripts-detail',
                       args=(obj.project.slug, obj.id),
                       request=self.context.get('request', None))
    class Meta:
        model = Document
        fields = ('id', 'description', 'url', 'project', 'last_updated',
                  'scans', 'transcript', 'related_topics', 'zotero_data',)

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
