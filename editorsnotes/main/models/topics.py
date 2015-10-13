# -*- coding: utf-8 -*-

from itertools import chain

from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models
import reversion

from editorsnotes.auth.models import ProjectPermissionsMixin

from .. import fields
from ..utils.markup import render_markup
from base import (
    Administered, CreationMetadata, LastUpdateMetadata, URLAccessible,
    IsReferenced)

__all__ = ['Topic', 'TopicAssignment']


class TopicMergeError(Exception):
    pass

#########################
# Main topic model #
#########################


class Topic(LastUpdateMetadata, URLAccessible, ProjectPermissionsMixin,
            IsReferenced, Administered):
    project = models.ForeignKey('Project', related_name='topics')

    # TODO: Make sure these are unique when saved
    types = ArrayField(models.URLField(), default=list)
    same_as = ArrayField(models.URLField(), default=list)
    alternate_names = ArrayField(models.CharField(max_length=200), default=list)

    preferred_name = models.CharField(max_length=200)
    related_topics = GenericRelation('TopicAssignment',
                                     related_query_name='assigned_to')

    markup = models.TextField(blank=True, null=True)
    markup_html = fields.XHTMLField(blank=True, null=True, editable=False)

    deleted = models.BooleanField(default=False, editable=False)
    merged_into = models.ForeignKey('self', blank=True, null=True,
                                    editable=False)

    class Meta:
        app_label = 'main'
        unique_together = (
            ('project', 'preferred_name'),
        )

    def as_text(self):
        return self.preferred_name

    @models.permalink
    def get_absolute_url(self):
        return ('api:topics-detail', [self.project.slug, self.id])

    def save(self, *args, **kwargs):
        if self.markup:
            self.markup_html = render_markup(self.markup, self.project)
        return super(Topic, self).save(*args, **kwargs)

    def get_affiliation(self):
        return self.project

    def has_markup(self):
        return self.markup is not None

    def get_referenced_items(self):
        from ..utils.markup_html import get_embedded_item_urls
        if not self.has_markup():
            return []

        urls_by_type = get_embedded_item_urls(self.markup_html)
        embedded_urls = set(chain(*urls_by_type.values()))
        return embedded_urls
reversion.register(Topic)


class TopicAssignment(CreationMetadata, ProjectPermissionsMixin):
    """
    An assignment of a topic to any other object, specific to a project.

    Optionally, a specific name can be used for an assignment, otherwise the
    projects' preferred name for that topic will be used.
    """
    topic = models.ForeignKey(Topic, blank=True, null=True,
                              related_name='assignments')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        app_label = 'main'
        unique_together = ('content_type', 'object_id', 'topic')

    def __unicode__(self):
        return u'{} --> {}: {}'.format(
            self.topic.preferred_name,
            self.content_object._meta.model_name,
            self.content_object)

    def get_affiliation(self):
        return self.topic.project
reversion.register(TopicAssignment)
