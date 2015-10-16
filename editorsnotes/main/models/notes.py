from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from licensing.models import License
import reversion

from editorsnotes.auth.models import ProjectPermissionsMixin, UpdatersMixin
from base import (Administered, LastUpdateMetadata, URLAccessible,
                  IsReferenced, ENMarkup)

__all__ = ['Note', 'NOTE_STATUS_CHOICES']

NOTE_STATUS_CHOICES = (
    ('0', 'closed'),
    ('1', 'open'),
    ('2', 'hibernating')
)


class Note(LastUpdateMetadata, Administered, URLAccessible, ENMarkup,
           IsReferenced, ProjectPermissionsMixin, UpdatersMixin):
    u"""
    Text written by an editor or curator. The text is stored as XHTML,
    so it may have hyperlinks and all the other features that XHTML
    enables.
    """
    title = models.CharField(max_length='80')

    project = models.ForeignKey('Project', related_name='notes')
    assigned_users = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                            blank=True, null=True)
    status = models.CharField(choices=NOTE_STATUS_CHOICES, max_length=1,
                              default='1')
    is_private = models.BooleanField(default=False)
    license = models.ForeignKey(License, blank=True, null=True)
    related_topics = GenericRelation('TopicAssignment')

    class Meta:
        app_label = 'main'
        ordering = ['-last_updated']
        permissions = (
            (u'view_private_note', u'Can view notes private to a project.'),
        )
        unique_together = (
            ('title', 'project'),
        )

    def as_text(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('api:notes-detail', [self.project.slug, self.id])

    def get_affiliation(self):
        return self.project

    def get_license(self):
        return self.license or self.project.default_license

    def has_topic(self, project_topic):
        return project_topic.id in \
            self.related_topics.values_list('topic_id', flat=True)


reversion.register(Note)
