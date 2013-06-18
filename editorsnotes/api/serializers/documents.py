import json

from rest_framework import serializers
from rest_framework.relations import RelatedField

from editorsnotes.main.models.documents import Document

class DocumentSerializer(serializers.ModelSerializer):
    topics = RelatedField('topics', many=True)
    zotero_data = serializers.CharField(required=False)
    class Meta:
        model = Document
        fields = ('id', 'description', 'zotero_data',)
    def validate_zotero_data(self, attrs, source):
        value = attrs.get(source, None)
        if value is not None:
            try:
                data = json.loads(value)
            except ValueError:
                err = 'Zotero data must be JSON value.'
                raise serializers.ValidationError(err)
            if 'itemType' not in data:
                err = 'Zotero data must at least include an itemType field.'
                raise serializers.ValidationError(err)
        return attrs
