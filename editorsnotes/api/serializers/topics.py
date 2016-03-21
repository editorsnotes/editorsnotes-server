from rest_framework import serializers
from rest_framework.reverse import reverse

from editorsnotes.main.models import Topic

from .. import fields
from ..validators import UniqueToProjectValidator
from ..ld import ROOT_NAMESPACE

from .mixins import EmbeddedItemsMixin, RelatedTopicSerializerMixin


__all__ = ['TopicSerializer', 'ENTopicSerializer']


class TopicSerializer(EmbeddedItemsMixin, serializers.ModelSerializer):
    url = fields.IdentityURLField(view_name='api:topics-detail')
    type = serializers.SerializerMethodField()
    wn_data = serializers.SerializerMethodField()
    linked_data = serializers.SerializerMethodField()
    project = fields.HyperlinkedAffiliatedProjectField(
        default=fields.CurrentProjectDefault())
    updaters = fields.UpdatersField()

    wn_aspect = fields.CustomLookupHyperlinkedField(
        view_name='api:topics-wn-detail',
        help_text='Working Notes-defined data for this topic.',
        lookup_kwarg_attrs={
            'project_slug': 'project.slug',
            'pk': 'pk'
        },
        read_only=True
    )

    project_aspect = fields.CustomLookupHyperlinkedField(
        view_name='api:topics-proj-detail',
        help_text='Project-defined data for this topic.',
        lookup_kwarg_attrs={
            'project_slug': 'project.slug',
            'pk': 'pk'
        },
        read_only=True
    )

    class Meta:
        model = Topic
        fields = (
            'id',
            'url',
            'type',
            'project',
            'updaters',
            'created',
            'last_updated',
            'wn_aspect',
            'project_aspect',
            'wn_data',
            'linked_data',

        )
        embedded_fields = (
            'project',
            'updaters',
        )

    def get_type(self, obj):
        return ROOT_NAMESPACE + 'Topic'

    def get_wn_data(self, obj):
        url = reverse(
            'api:topics-wn-detail',
            args=[obj.project.slug, obj.pk],
            request=self.context['request'])
        return {
            '@graph': {
                '@id': url,
                '@graph': ENTopicSerializer(obj, context=self.context).data
            }
        }

    def get_linked_data(self, obj):
        url = reverse(
            'api:topics-proj-detail',
            args=[obj.project.slug, obj.pk],
            request=self.context['request'])
        return {
            '@graph': {
                '@id': url,
                '@graph': obj.ld
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
