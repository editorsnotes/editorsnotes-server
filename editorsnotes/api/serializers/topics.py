from rest_framework import serializers
from rest_framework.reverse import reverse

from editorsnotes.main.models import Topic

from .. import fields
from ..validators import UniqueToProjectValidator

from .mixins import EmbeddedItemsMixin, RelatedTopicSerializerMixin


__all__ = ['TopicSerializer', 'ENTopicSerializer']


class TopicSerializer(EmbeddedItemsMixin, serializers.ModelSerializer):
    url = fields.IdentityURLField(view_name='api:topics-detail')
    data = serializers.SerializerMethodField()
    aspects = serializers.SerializerMethodField()
    project = fields.HyperlinkedAffiliatedProjectField(
        default=fields.CurrentProjectDefault())
    updaters = fields.UpdatersField()

    class Meta:
        model = Topic
        fields = (
            'id',
            'url',
            'project',
            'updaters',
            'created',
            'last_updated',
            'aspects',
            'data',

        )
        embedded_fields = (
            'project',
            'updaters',
        )

    def get_aspects(self, obj):
        return [
            reverse('api:topics-wn-detail',
                    args=[obj.project.slug, obj.pk],
                    request=self.context['request']),
            reverse('api:topics-proj-detail',
                    args=[obj.project.slug, obj.pk],
                    request=self.context['request'])
        ]

    def get_data(self, obj):
        en_topic_url, project_topic_url = self.get_aspects(obj)
        return {
            en_topic_url: {
                "@id": en_topic_url,
                "@graph": ENTopicSerializer(obj, context=self.context).data
            },
            project_topic_url: {
                "@id": project_topic_url,
                "@graph": {}
            }
        }


class ENTopicSerializer(RelatedTopicSerializerMixin, EmbeddedItemsMixin,
                        serializers.ModelSerializer):
    url = fields.IdentityURLField(view_name='api:topics-detail')
    related_topics = fields.TopicAssignmentField(many=True)

    references = fields.UnqualifiedURLField(
        source='get_referenced_items')
    referenced_by = fields.UnqualifiedURLField(
        source='get_referencing_items')

    class Meta:
        model = Topic
        fields = (
            'url',
            'preferred_name',
            'alternate_names',

            'related_topics',

            'markup',
            'markup_html',

            'references',
            'referenced_by',
        )
        embedded_fields = (
            'related_topics',
            'references',
            'referenced_by',
        )
        validators = [UniqueToProjectValidator('preferred_name')]
