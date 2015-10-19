from collections import OrderedDict
from itertools import chain
import json
from urlparse import urlparse

from django.core.urlresolvers import resolve

from rest_framework.renderers import JSONRenderer

from editorsnotes.auth.models import User
from editorsnotes.search.items.helpers import get_data_for_urls

ensure_list = lambda val: [val] if isinstance(val, basestring) else val


class EmbeddedItemsMixin(object):
    def __init__(self, *args, **kwargs):
        self.include_embeds = kwargs.pop('include_embeds', False)
        return super(EmbeddedItemsMixin, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        data = super(EmbeddedItemsMixin, self).to_representation(instance)

        if self.include_embeds:
            embedded_fields = getattr(self.Meta, 'embedded_fields', [])
            urls = [ensure_list(data[key]) for key in embedded_fields]
            urls = set(chain.from_iterable(urls))

            users_base = self.context['request'].build_absolute_uri('/users/')

            user_urls = {url for url in urls if url.startswith(users_base)}
            urls = urls.difference(user_urls)

            embedded_data = OrderedDict()
            for key, val in get_data_for_urls(urls).items():
                embedded_data[key] = val

            for key, val in self.get_users_from_urls(user_urls).items():
                embedded_data[key] = val

            data['embedded'] = embedded_data

        return data

    def get_users_from_urls(self, urls):
        from editorsnotes.api.serializers import UserSerializer
        urls = list(urls)
        urls.sort()

        if not urls:
            return {}

        usernames = [
            resolve(urlparse(url).path).kwargs['username']
            for url in urls
        ]

        qs = User.objects.filter(username__in=usernames)

        serializer = UserSerializer(instance=qs, many=True,
                                    context=self.context)
        data = json.loads(JSONRenderer().render(serializer.data),
                          object_pairs_hook=OrderedDict)

        ret = OrderedDict()
        for i, url in enumerate(urls):
            ret[url] = data[i]

        return ret


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
