from rest_framework import serializers

from editorsnotes.auth.models import Project, User

from ..fields import CustomLookupHyperlinkedField, IdentityURLField


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


class UserSerializer(serializers.ModelSerializer):
    url = IdentityURLField()

    class Meta:
        model = User
        fields = (
            'url',
            'profile',
            'display_name',
            'date_joined',
            'last_login'

            # FIXME
            # 'projects', (or groups, roles)
            # 'email',
            # 'markup',
            # 'markup_html',
            # 'references'
        )
