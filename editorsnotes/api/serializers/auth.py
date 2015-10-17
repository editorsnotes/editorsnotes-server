from rest_framework import serializers

from editorsnotes.auth.models import Project, User

from ..fields import CustomLookupHyperlinkedField, IdentityURLField
from ..ld import ROOT_NAMESPACE
from .base import EmbeddedItemsMixin


__all__ = ['ProjectSerializer', 'UserSerializer']


class ProjectSerializer(serializers.ModelSerializer):
    url = IdentityURLField()

    type = serializers.SerializerMethodField()

    notes = CustomLookupHyperlinkedField(
        view_name='api:notes-list',
        lookup_kwarg_attrs={'project_slug': 'slug'},
        read_only=True
    )

    topics = CustomLookupHyperlinkedField(
        view_name='api:topics-list',
        lookup_kwarg_attrs={'project_slug': 'slug'},
        read_only=True
    )

    documents = CustomLookupHyperlinkedField(
        view_name='api:documents-list',
        lookup_kwarg_attrs={'project_slug': 'slug'},
        read_only=True
    )

    activity = CustomLookupHyperlinkedField(
        view_name='api:projects-activity',
        lookup_kwarg_attrs={'project_slug': 'slug'},
        read_only=True
    )

    class Meta:
        model = Project
        fields = (
            'url',
            'type',

            'name',
            'markup',
            'markup_html',

            'notes',
            'topics',
            'documents',
            'activity',

            # FIXME
            # 'featured_items',
            # 'references',
        )

    def get_type(self, obj):
        return ROOT_NAMESPACE + 'Project'



class UserSerializer(EmbeddedItemsMixin, serializers.ModelSerializer):
    url = IdentityURLField()

    type = serializers.SerializerMethodField()

    projects = serializers.HyperlinkedRelatedField(
        source='get_affiliated_projects',
        many=True,
        read_only=True,
        view_name='api:projects-detail',
        lookup_field='slug',
        lookup_url_kwarg='project_slug'
    )

    activity = serializers.HyperlinkedRelatedField(
        source='*',
        read_only=True,
        view_name='api:users-activity',
        lookup_field='username',
        lookup_url_kwarg='username'
    )

    class Meta:
        model = User
        fields = (
            'url',
            'profile',

            'projects',

            'activity',
            'display_name',
            'date_joined',
            'last_login'

            # FIXME
            # 'email',
        )
        embedded_fields = ('projects',)

    def get_type(self, obj):
        return ROOT_NAMESPACE + 'User'
