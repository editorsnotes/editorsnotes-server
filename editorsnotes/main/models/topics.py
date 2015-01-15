# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models, transaction
import reversion

from .. import fields, utils
from auth import Project, ProjectPermissionsMixin
from base import (
    Administered, CreationMetadata, LastUpdateMetadata, URLAccessible)

__all__ = ['Topic', 'TopicNode', 'TopicAssignment', 'AlternateName',
           'LegacyTopic']

TYPE_CHOICES = (
    ('EVT', 'Event'),
    ('ORG', 'Organization'),
    ('PER', 'Person'),
    ('PUB', 'Publication')
)

class TopicMergeError(Exception):
    pass

#########################
# Main topic node model #
#########################

class TopicNodeManager(models.Manager):
    def for_project(self, project):
        return self.select_related('project_topics')\
                .filter(project_topics__project_id=project.id)

class TopicNode(LastUpdateMetadata, URLAccessible):
    """
    The container for projects' connections to topics.

    A Topic can be described as a person, organization, place, event,
    publication, or a generic topic/theme. The names of topics are contained in
    a separate model, but Topic nodes are identified site-wide with the most
    common names used by projects to refer to them.

    When all connections between a Topic node and projects are removed (either
    through simple deletion or merging), we can classify that Topic node as
    "empty". Instead of deleting the model, however, we specify that it was
    deleted and optionally point to the new Topic node that it was merged into.
    """
    _preferred_name = models.CharField(max_length='200')
    type = models.CharField(max_length=3, choices=TYPE_CHOICES, blank=True, null=True)
    deleted = models.BooleanField(default=False, editable=False)
    merged_into = models.ForeignKey('self', blank=True, null=True, editable=False)
    objects = TopicNodeManager()
    class Meta:
        app_label = 'main'
    def as_text(self):
        return self.preferred_name
    @models.permalink
    def get_absolute_url(self):
        return ('topic_node_view', [self.id])
    @property
    def preferred_name(self):
        return self._preferred_name
    def get_connected_projects(self):
        return Project.objects.filter(
            id__in=self.project_topics.values_list('project_id', flat=True))
    def related_objects(self, model=None):
        qs = TopicAssignment.objects.filter(topic__topic_node_id=self.id)
        if model is not None:
            model_ct = ContentType.objects.get_for_model(model)
            model_assignments = qs.filter(content_type_id=model_ct.id)
            return model.objects.filter(
                id__in=model_assignments.values_list('object_id', flat=True)
            )
        else:
            return [obj.content_object for obj in qs]
reversion.register(TopicNode)


#################################
# Project-specific topic models #
#################################

class TopicManager(models.Manager):
    def create_along_with_node(self, preferred_name, project, user, type=None,
                               **kwargs):
        """
        Create a new topic node and a container with the given name.

        Returns the node and the container.
        """
        topic_node = TopicNode.objects.create(_preferred_name=preferred_name,
                                              creator=user,
                                              last_updater=user,
                                              type=type)
        return topic_node, self.create(topic_node_id=topic_node.id,
                                       project_id=project.id,
                                       preferred_name=preferred_name,
                                       creator_id=user.id,
                                       last_updater_id=user.id,
                                       **kwargs)
    def create_from_node(self, topic_node, project, user, name=None):
        """
        Given a topic node, create a new container for a project.

        If no name is passed, the (cached) preferred name of the topic node will
        be used as the container's preferred name.
        """
        return self.create(topic_node=topic_node, project=project,
                           creator=user, last_updater=user,
                           preferred_name=name or topic_node.preferred_name)
    def get_or_create_by_name(self, name, project, user):
        qs = self.filter(preferred_name=name, project=project)
        if qs.exists():
            return qs.get()
        node, topic = self.create_along_with_node(name, project, user)
        return topic
    def get_or_create_from_node(self, topic_node, project, user, name=None):
        """
        Given a topic node, get or create a container for a project.

        Returns (created (bool), container (ProjectTopicContainer))

        If a topic container is created and no name is passed to the function,
        the (cached) preferred name of the topic node will be used as the
        container's preferred name.
        """
        defaults = {'creator': user, 'last_updater': user,
                    'preferred_name': name or topic_node.preferred_name}
        return self.get_or_create(topic_node=topic_node, project=project,
                                  defaults=defaults)

class Topic(LastUpdateMetadata, URLAccessible, ProjectPermissionsMixin,
            Administered):
    project = models.ForeignKey('Project', related_name='topics')
    topic_node = models.ForeignKey(TopicNode, related_name='project_topics')
    preferred_name = models.CharField(max_length=200)
    related_topics = GenericRelation('TopicAssignment', related_query_name='assigned_to')
    summary = fields.XHTMLField(blank=True, null=True)
    summary_cites = GenericRelation('Citation')
    deleted = models.BooleanField(default=False, editable=False)
    merged_into = models.ForeignKey('self', blank=True, null=True, editable=False)
    objects = TopicManager()
    class Meta:
        app_label = 'main'
        unique_together = (
            ('project', 'preferred_name'),
            ('project', 'topic_node')
        )
    def as_text(self):
        return self.preferred_name
    @models.permalink
    def get_absolute_url(self):
        return ('topic_view', [self.project.slug, self.topic_node_id])
    def get_admin_url(self):
        return reverse(
            'admin:main_topic_change', args=(self.project.slug, self.topic_node_id))
    def get_affiliation(self):
        return self.project
    def has_summary(self):
        return self.summary is not None
    def clean_fields(self, exclude=None):
        super(Topic, self).clean_fields(exclude=exclude)
        if 'summary' not in exclude and self.has_summary():
            utils.remove_stray_brs(self.summary)
            utils.remove_empty_els(self.summary)
            if not self.summary.xpath('string()').strip():
                self.summary = None
    def validate_unique(self, exclude=None):
        super(Topic, self).validate_unique(exclude)
        qs = self.__class__.objects.filter(
            preferred_name=self.preferred_name, project_id=self.project.id)
        if self.id:
            qs = qs.exclude(id=self.id)
        if qs.exists():
            raise ValidationError({
                'preferred_name': [u'Topic with this preferred name '
                                   'already exists.']
            })

        qs = self.__class__.objects.filter(
            topic_node_id=self.topic_node_id, project_id=self.project.id)
        if self.id:
            qs = qs.exclude(id=self.id)
        if qs.exists():
            raise ValidationError({
                '__all__': [u'This project is already connected with topic '
                            'node {}.'.format(self.topic_node)]
            })
            
    @transaction.atomic
    def merge_into(self, target):
        """
        Merge all connections from this container into another.
        """
        if self.project_id != target.project_id:
            raise TopicMergeError(
                'Can only merge topics within the same project.')
        if not isinstance(target, Topic):
            raise ValueError('Target must be another Topic')

        # Move summary to new container if it exists
        if self.has_summary():
            if target.has_summary():
                raise TopicMergeError(
                    'Can\'t merge two summaries. Delete a summary before continuing.')
            target.summary = self.summary
        for cite in self.summary_cites.all():
            cite.object_id = target.id
            cite.save()

        # Move topic assignments to the new container, but only if those
        # assignments don't already exist in the target.
        assignments = (
            ta for ta in self.assignments.all()
            if (ta.content_type_id, ta.object_id) not in
            target.related_topics.values_list('content_type_id', 'object_id')
        )
        for assignment in assignments:
            assignment.topic_id = target.id
            assignment.save()
        for stale_assignment in self.related_topics.all():
            stale_assignment.delete()

        # If no projects point to origin's topic node anymore, merge it into the
        # target's topic node.
        other_containers_exist = self.topic_node.project_topics\
                .filter(deleted=False)\
                .exclude(id=self.id)\
                .exists()
        if not other_containers_exist:
            self.topic_node.deleted = True
            self.topic_node.merged_into = target.topic_node
            self.topic_node.save()

        # Point this topic toward the new one.
        self.deleted = True
        self.merged_into = target
        self.save()

        return target
reversion.register(Topic)

class AlternateName(CreationMetadata, ProjectPermissionsMixin):
    topic = models.ForeignKey(Topic, related_name='alternate_names')
    name = models.CharField(max_length=200)
    class Meta:
        app_label = 'main'
        unique_together = ('topic', 'name',)
    def __unicode__(self):
            return self.name

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
    @property
    def topic_node(self):
        return self.topic.topic_node
    @property
    def topic_node_id(self):
        return self.topic.topic_node_id
    def __unicode__(self):
        return u'{} --> {}: {}'.format(
            self.topic.preferred_name,
            self.content_object._meta.model_name,
            self.content_object)
    def get_affiliation(self):
        return self.topic.project
reversion.register(TopicAssignment)


##############################################################
# Legacy topic models (will be removed after data migration) #
##############################################################

class LegacyTopic(models.Model, URLAccessible):
    """ 
    A controlled topic such as a person name, an organization name, a
    place name, an event name, a publication name, or the name of a
    topic or theme.
    """
    preferred_name = models.CharField(max_length='80', unique=True)
    slug = models.CharField(max_length='80', unique=True, editable=False, db_index=True)
    merged_into = models.ForeignKey(TopicNode, blank=True, null=True, editable=False)
    class Meta:
        app_label = 'main'
        ordering = ['slug']
    @models.permalink
    def get_absolute_url(self):
        return ('legacy_topic_view', [self.slug])
    def as_text(self):
        return 'DEPRECATED: {}'.format(self.preferred_name)
