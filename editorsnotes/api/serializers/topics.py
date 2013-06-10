from rest_framework import serializers
from rest_framework.relations import RelatedField
from editorsnotes.main.models.topics import Topic, ProjectTopicContainer

class TopicSerializer(serializers.ModelSerializer):
    topics = RelatedField('topics', many=True)
    creator = serializers.Field(source='creator.username')
    last_updater = serializers.Field(source='last_updater.username')
    class Meta:
        model = main_models.Topic
        fields = ('id', 'preferred_name', 'type', 'topics', 'summary',
                  'creator', 'last_updater')

