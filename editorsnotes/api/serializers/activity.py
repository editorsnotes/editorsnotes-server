from rest_framework import serializers

from editorsnotes.auth.models import (LogActivity, ADDITION, CHANGE,
                                      DELETION)

__all__ = ['ActivitySerializer']

VERSION_ACTIONS = {
    ADDITION: 'added',
    CHANGE: 'changed',
    DELETION: 'deleted'
}

# TODO: make these fields nested, maybe
class ActivitySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    project = serializers.ReadOnlyField(source='project.slug')
    type = serializers.ReadOnlyField(source='content_type.model')
    url = serializers.SerializerMethodField('get_object_url')
    title = serializers.ReadOnlyField(source='display_title')
    action = serializers.SerializerMethodField('get_action_repr')
    class Meta:
        model = LogActivity
        fields = ('user', 'project', 'time', 'type', 'url', 'title', 'action',)
    def get_object_url(self, obj):
        if obj.action == DELETION or obj.content_object is None:
            return None
        else:
            return obj.content_object.get_absolute_url()
    def get_action_repr(self, version_obj):
        return VERSION_ACTIONS[version_obj.action]
