from ..fields import EmbeddedItemsURLField, EmbeddedItemsSerializedField


class EmbeddedMarkupReferencesMixin(object):
    def __init__(self, *args, **kwargs):
        embed_style = kwargs.pop('embed_style', None)
        super(EmbeddedMarkupReferencesMixin, self).__init__(*args, **kwargs)

        if embed_style is None:
            return

        if embed_style == 'urls':
            field = EmbeddedItemsURLField
        elif embed_style == 'nested':
            field = EmbeddedItemsSerializedField
        else:
            raise ValueError('Bad value for `embed_style`. Must be "urls" or '
                             "nested")

        self.fields['_embedded'] = field(source='markup_html')


class RelatedTopicSerializerMixin(object):
    def save_related_topics(self, obj, topics):
        """
        Given an array of names, make sure obj is related to those topics.
        """
        rel_topics = obj.related_topics.select_related('topic').all()

        new_topics = set(topics)
        existing_topics = {ta.topic for ta in rel_topics}

        to_create = new_topics.difference(existing_topics)
        to_delete = existing_topics.difference(new_topics)

        # Delete unused topic assignments
        rel_topics.filter(topic__in=to_delete).delete()

        # Create new topic assignments
        for topic in to_create:
            obj.related_topics.create(
                topic=topic, creator_id=self.context['request'].user.id)

    def create(self, validated_data):
        topics = validated_data.pop('related_topics', None)
        obj = super(RelatedTopicSerializerMixin, self).create(validated_data)
        if topics is not None:
            self.save_related_topics(obj, topics)
        return obj

    def update(self, instance, validated_data):
        topics = validated_data.pop('related_topics', None)
        super(RelatedTopicSerializerMixin, self)\
            .update(instance, validated_data)
        if topics is not None:
            self.save_related_topics(instance, topics)
        return instance
