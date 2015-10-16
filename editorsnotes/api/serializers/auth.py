from rest_framework import serializers

from editorsnotes.auth.models import Project, User

from ..fields import CustomLookupHyperlinkedField, IdentityURLField
from .base import EmbeddedItemsMixin


__all__ = ['ProjectSerializer', 'UserSerializer']


class ProjectSerializer(serializers.ModelSerializer):
    url = IdentityURLField()

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


class UserSerializer(EmbeddedItemsMixin, serializers.ModelSerializer):
    url = IdentityURLField()

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
