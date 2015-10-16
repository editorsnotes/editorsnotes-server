# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models
import reversion

from editorsnotes.auth.models import ProjectPermissionsMixin, UpdatersMixin

from base import (
    Administered, CreationMetadata, LastUpdateMetadata, URLAccessible,
    IsReferenced, ENMarkup)

__all__ = ['Topic', 'TopicAssignment']


class TopicMergeError(Exception):
    pass

#########################
# Main topic model #
#########################


class Topic(LastUpdateMetadata, URLAccessible, ProjectPermissionsMixin,
            UpdatersMixin, IsReferenced, Administered, ENMarkup):
    project = models.ForeignKey('Project', related_name='topics')

    # TODO: Make sure these are unique when saved
    types = ArrayField(models.URLField(), default=list)
    same_as = ArrayField(models.URLField(), default=list)
    alternate_names = ArrayField(models.CharField(max_length=200),
                                 default=list)

    preferred_name = models.CharField(max_length=200)
    related_topics = GenericRelation('TopicAssignment',
                                     related_query_name='assigned_to')

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

    def get_affiliation(self):
        return self.project
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
