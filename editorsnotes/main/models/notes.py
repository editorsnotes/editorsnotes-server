from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from licensing.models import License
from reversion import revisions as reversion

from editorsnotes.auth.models import ProjectPermissionsMixin, UpdatersMixin
from .base import (Administered, LastUpdateMetadata, URLAccessible,
                  IsReferenced, ENMarkup)

__all__ = ['Note', 'NOTE_STATUS_CHOICES']

NOTE_STATUS_CHOICES = (
    ('0', 'closed'),
    ('1', 'open'),
    ('2', 'hibernating')
)


class Note(LastUpdateMetadata, Administered, URLAccessible, ENMarkup,
           IsReferenced, ProjectPermissionsMixin, UpdatersMixin):
    """
    Text written by an editor or curator. The text is stored as XHTML,
    so it may have hyperlinks and all the other features that XHTML
    enables.
    """
    title = models.CharField(
        max_length=80,
        help_text=(
            'The title of the note.'
        )
    )

    project = models.ForeignKey(
        'Project',
        related_name='notes',
        help_text=(
            'The project to which this note belongs.'
        )
    )
    assigned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        help_text=(
            'Users who have been assigned to this note.'
        )
    )
    status = models.CharField(
        choices=NOTE_STATUS_CHOICES, max_length=1, default='1',
        help_text=(
            'The status of the note. "Open" for outstanding, "Closed" for '
            'finished, or "Hibernating" for somewhere in between.'
        )
    )
    is_private = models.BooleanField(
        default=False,
        help_text=(
            'If true, will only be be viewable to users who belong to the '
            'note\'s project.'
        )
    )
    license = models.ForeignKey(
        License, blank=True, null=True,
        help_text=(
            'The license under which this note is available.'
        )
    )
    related_topics = GenericRelation(
        'TopicAssignment',
        help_text=(
            'Topics under which this note is indexed.'
        )
    )

    class Meta:
        app_label = 'main'
        ordering = ['-last_updated']
        permissions = (
            ('view_private_note', 'Can view notes private to a project.'),
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
