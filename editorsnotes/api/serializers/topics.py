from rest_framework import serializers

from editorsnotes.main.models import Topic

from .. import fields
from ..ld import ROOT_NAMESPACE
from ..validators import UniqueToProjectValidator

from .mixins import EmbeddedItemsMixin, RelatedTopicSerializerMixin


__all__ = ['TopicSerializer']


class TopicSerializer(RelatedTopicSerializerMixin, EmbeddedItemsMixin,
                      serializers.ModelSerializer):
    url = fields.IdentityURLField()
    type = serializers.SerializerMethodField()
    project = fields.HyperlinkedAffiliatedProjectField(
        default=fields.CurrentProjectDefault())
    updaters = fields.UpdatersField()

    related_topics = fields.TopicAssignmentField(many=True)

    references = fields.UnqualifiedURLField(
        source='get_referenced_items')
    referenced_by = fields.UnqualifiedURLField(
        source='get_referencing_items')

    class Meta:
        model = Topic
        fields = (
            'id',
            'url',
            'type',
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

    def get_type(self, obj):
        return ROOT_NAMESPACE + 'Topic'
