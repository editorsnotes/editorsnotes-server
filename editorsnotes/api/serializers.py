from rest_framework import serializers
from rest_framework.relations import (
    RelatedField, PrimaryKeyRelatedField, HyperlinkedRelatedField)
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
    creator = serializers.Field(source='creator.username')
    last_updater = serializers.Field(source='last_updater.username')
    class Meta:
        model = main_models.Document
        fields = ('id', 'description', 'creator', 'last_updater')

class NoteSerializer(serializers.ModelSerializer):
    topics = RelatedField('topics', many=True)
    creator = serializers.Field(source='creator.username')
    last_updater = serializers.Field(source='last_updater.username')
    class Meta:
        model = main_models.Note
        fields = ('id', 'title', 'topics', 'content', 'status',
                  'creator', 'last_updater')
