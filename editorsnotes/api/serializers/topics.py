from rest_framework import serializers

from editorsnotes.main.models import Topic

from ..fields import (CurrentProjectDefault, HyperlinkedAffiliatedProjectField,
                      UnqualifiedURLField, TopicAssignmentField, UpdatersField,
                      IdentityURLField)
from ..validators import UniqueToProjectValidator

from .base import EmbeddedItemsMixin, RelatedTopicSerializerMixin


__all__ = ['TopicSerializer']


class TopicSerializer(RelatedTopicSerializerMixin, EmbeddedItemsMixin,
                      serializers.ModelSerializer):
    url = IdentityURLField()
    project = HyperlinkedAffiliatedProjectField(
        default=CurrentProjectDefault())
    updaters = UpdatersField()

    related_topics = TopicAssignmentField(many=True)

    references = UnqualifiedURLField(source='get_referenced_items')
    referenced_by = UnqualifiedURLField(source='get_referencing_items')

    class Meta:
        model = Topic
        fields = (
            'id',
            'url',
            'project',

            'preferred_name',

            'created',
            'last_updated',
            'updaters',

            'types',
            'same_as',
            'alternate_names',

            'markup',
            'markup_html',

            'related_topics',
            'references',
            'referenced_by',
        )
        embedded_fields = (
            'project',
            'updaters',

            'related_topics',
            'references',
            'referenced_by',
        )
        validators = [UniqueToProjectValidator('preferred_name')]

    def __init__(self, *args, **kwargs):
        minimal = kwargs.pop('minimal', False)
        super(TopicSerializer, self).__init__(*args, **kwargs)
        if minimal:
            self.fields.pop('markup')
            self.fields.pop('markup_html')
            self.fields.pop('_embedded', None)
