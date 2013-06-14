from rest_framework import serializers
from rest_framework.relations import RelatedField

from editorsnotes.main.models.documents import Document

class DocumentSerializer(serializers.ModelSerializer):
    topics = RelatedField('topics', many=True)
    class Meta:
        model = Document
        fields = ('id', 'description',)
