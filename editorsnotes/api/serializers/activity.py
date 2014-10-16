from reversion.models import Version, VERSION_ADD, VERSION_CHANGE, VERSION_DELETE
from rest_framework import serializers

VERSION_ACTIONS = {
    VERSION_ADD: 'added',
    VERSION_CHANGE: 'changed',
    VERSION_DELETE: 'deleted'
}

# TODO: make these fields nested, maybe
class ActivitySerializer(serializers.ModelSerializer):
    user = serializers.Field(source='revision.user.username')
    project = serializers.Field(source='revision.project_metadata.project.slug')
    time = serializers.Field(source='revision.date_created')
    type = serializers.Field(source='content_type.model')
    url = serializers.SerializerMethodField('get_object_url')
    title = serializers.Field(source='object_repr')
    action = serializers.SerializerMethodField('get_action_repr')
    class Meta:
        model = Version
        fields = ('user', 'project', 'time', 'type', 'url', 'title', 'action',)
    def get_object_url(self, version_obj):
        return version_obj.object and version_obj.object.get_absolute_url()
    def get_action_repr(self, version_obj):
        return VERSION_ACTIONS[version_obj.type]
