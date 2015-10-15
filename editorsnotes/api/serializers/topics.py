from rest_framework import serializers

from editorsnotes.main.models import Topic

from ..fields import (CurrentProjectDefault, HyperlinkedAffiliatedProjectField,
                      UnqualifiedURLField, TopicAssignmentField,
                      IdentityURLField)
from ..validators import UniqueToProjectValidator

from .base import EmbeddedItemsMixin, RelatedTopicSerializerMixin


__all__ = ['TopicSerializer']


class TopicSerializer(RelatedTopicSerializerMixin, EmbeddedItemsMixin,
                      serializers.ModelSerializer):
    url = IdentityURLField()

    project = HyperlinkedAffiliatedProjectField(
        default=CurrentProjectDefault())

    related_topics = TopicAssignmentField(required=False)

    references = UnqualifiedURLField(source='get_referenced_items')
    referenced_by = UnqualifiedURLField(source='get_referencing_items')

    class Meta:
        embedded_fields = ('project', 'references', 'referenced_by',
                           'related_topics',)
        model = Topic
        fields = ('id', 'url', 'preferred_name', 'types', 'same_as',
                  'alternate_names', 'related_topics', 'project',
                  'last_updated', 'markup', 'markup_html', 'references',
                  'referenced_by',)
        validators = [UniqueToProjectValidator('preferred_name')]

    def __init__(self, *args, **kwargs):
        minimal = kwargs.pop('minimal', False)
        super(TopicSerializer, self).__init__(*args, **kwargs)
        if minimal:
            self.fields.pop('markup')
            self.fields.pop('markup_html')
            self.fields.pop('_embedded', None)
