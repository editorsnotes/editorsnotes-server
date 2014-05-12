from collections import OrderedDict
import json

from lxml import etree
from rest_framework import serializers
from rest_framework.reverse import reverse

from editorsnotes.main.models import Document, Citation, Scan

from .base import (
    RelatedTopicSerializerMixin, ProjectSpecificItemMixin, URLField,
    ProjectSlugField)

class ZoteroField(serializers.WritableField):
    def to_native(self, zotero_data):
        return zotero_data and json.loads(zotero_data,
                                          object_pairs_hook=OrderedDict)
    def from_native(self, data):
        return data and json.dumps(data)

class HyperLinkedImageField(serializers.ImageField):
    def to_native(self, value):
        if not value.name:
            return None

        if 'request' in self.context:
            return self.context['request'].build_absolute_uri(value.url)
        else:
            return value.url

class ScanSerializer(serializers.ModelSerializer):
    creator = serializers.Field('creator.username')
    image = HyperLinkedImageField()
    image_thumbnail = HyperLinkedImageField(read_only=True)
    class Meta:
        model = Scan
        fields = ('id', 'image', 'image_thumbnail', 'ordering', 'created',
                  'creator',)

class DocumentSerializer(RelatedTopicSerializerMixin, ProjectSpecificItemMixin,
                         serializers.ModelSerializer):
    project = ProjectSlugField()
    zotero_data = ZoteroField(required=False)
    url = URLField()
    scans = ScanSerializer(many=True, required=False, read_only=True)
    class Meta:
        model = Document
        fields = ('id', 'description', 'url', 'project', 'last_updated',
                  'scans', 'related_topics', 'zotero_data',)

class CitationSerializer(serializers.ModelSerializer):
    document = serializers.SerializerMethodField('get_document_url')
    document_description = serializers.SerializerMethodField('get_document_description')
    class Meta:
        model = Citation
        fields = ('id', 'document', 'document_description', 'notes')
    def get_document_description(self, obj):
        return etree.tostring(obj.document.description)
    def get_document_url(self, obj):
        request = self.context['request']
        return reverse('api:api-documents-detail',
                       args=[request.project.slug, obj.document_id],
                       request=request)

