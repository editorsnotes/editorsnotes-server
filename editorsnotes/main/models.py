# -*- coding: utf-8 -*-

import re
import utils
import fields
from copy import deepcopy
from lxml import etree
from unaccent import unaccent
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core import urlresolvers
from django.core.exceptions import ValidationError
from django.core.urlresolvers import NoReverseMatch
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

# -------------------------------------------------------------------------------
# Abstract base classes and interfaces.
# -------------------------------------------------------------------------------

class CreationMetadata(models.Model):
    creator = models.ForeignKey(User, editable=False, related_name='created_%(class)s_set')
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True
        get_latest_by = 'created'

class LastUpdateMetadata(CreationMetadata):
    last_updater = models.ForeignKey(User, editable=False, related_name='last_to_update_%(class)s_set')
    last_updated = models.DateTimeField(auto_now=True)    
    class Meta:
        abstract = True

class Administered():
    def get_admin_url(self):
        return urlresolvers.reverse(
            'admin:main_%s_change' % self._meta.module_name, args=(self.id,))

class URLAccessible():
    @models.permalink
    def get_absolute_url(self):
        return ('%s_view' % self._meta.module_name, [str(self.id)])
    def __unicode__(self):
        return utils.truncate(self.as_text())
    def as_text(self):
        raise Exception('Must implement %s.as_text()' % self._meta.module_name)
    def as_html(self):
        return '<span class="%s">%s</span>' % (
            self._meta.module_name, conditional_escape(self.as_text()))

# -------------------------------------------------------------------------------
# Primary models. These have their own URLs and administration interfaces.
# -------------------------------------------------------------------------------

class Source(LastUpdateMetadata, Administered, URLAccessible):
    u"""
    A documented source for assertions made in notes. 
    """
    description = fields.XHTMLField()
    type = models.CharField(max_length=1, choices=(('P','primary source'),('S','secondary source')), default='S')
    ordering = models.CharField(max_length=32, editable=False)
    url = models.URLField(blank=True, verify_exists=True)
    @property
    def transcript(self):
        try:
            return self._transcript
        except Transcript.DoesNotExist:
            return None
    def as_text(self):
        return utils.xhtml_to_text(self.description)
    def as_html(self):
        return mark_safe(
            '<div class="source">%s</div>' % etree.tostring(self.description))
    def save(self, *args, **kwargs):
        self.ordering = re.sub(r'[^\w\s]', '', utils.xhtml_to_text(self.description))[:32]
        super(Source, self).save(*args, **kwargs)
    class Meta:
        ordering = ['ordering']    

class Transcript(LastUpdateMetadata, Administered, URLAccessible):
    u"""
    A text transcript of a primary source document.
    """
    source = models.OneToOneField(Source, related_name='_transcript')
    content = fields.XHTMLField()
    def get_absolute_url(self):
        # Transcripts don't have their own URLs; use the document URL.
        return '%s#transcript' % self.source.get_absolute_url()
    def as_text(self):
        return self.source.as_text()
    def as_html(self):
        return self.source.as_html()

class Footnote(LastUpdateMetadata, Administered, URLAccessible):
    u"""
    A footnote attached to a transcript.
    """
    transcript = models.ForeignKey(Transcript, related_name='footnotes')
    content = fields.XHTMLField()
    def footnoted_text(self):
        try:
            selector = 'a.footnote[href="%s"]' % self.get_absolute_url()
            results = self.transcript.content.cssselect(selector)
            if len(results) == 1:
                return results[0].xpath('string()')
        except NoReverseMatch: # footnote has been deleted
            pass
        return None 
    def as_text(self):
        footnoted_text = self.footnoted_text()
        if footnoted_text is None:
            return utils.xhtml_to_text(self.content)
        else:
            return u'"%s"' % footnoted_text
    def remove_self_from(self, transcript):
        selector = 'a.footnote[href="%s"]' % self.get_absolute_url()
        results = transcript.content.cssselect(selector)
        if len(results) == 1:
            results[0].drop_tag()
    def delete(self, *args, **kwargs):
        self.remove_self_from(self.transcript)
        self.transcript.save()
        super(Footnote, self).delete(*args, **kwargs)

class Topic(LastUpdateMetadata, Administered, URLAccessible):
    """ 
    A controlled topic such as a person name, an organization name, a
    place name, an event name, a publication name, or the name of a
    topic or theme.
    """
    preferred_name = models.CharField(max_length='80', unique=True)
    slug = models.CharField(max_length='80', unique=True, editable=False)
    related_topics = models.ManyToManyField('self', blank=True)
    summary = fields.XHTMLField(verbose_name='article')
    summary_citations = generic.GenericRelation('Citation')
    def __init__(self, *args, **kwargs):
        super(Topic, self).__init__(*args, **kwargs)
        if 'preferred_name' in kwargs:
            self.slug = self._make_slug(kwargs['preferred_name'])
    def _make_slug(self, preferred_name):
        return '-'.join(
            [ x for x in re.split('\W+', unaccent(unicode(preferred_name)))
              if len(x) > 0 ]).lower()
    def __setattr__(self, key, value):
        super(Topic, self).__setattr__(key, value)
        if key == 'preferred_name':
            self.slug = self._make_slug(value)
    def get_aliases(self):
        return u' '.join([ a.name for a in self.aliases.all() ])
    @models.permalink
    def get_absolute_url(self):
        return ('topic_view', [str(self.slug)])
    def as_text(self):
        return self.preferred_name
    def validate_unique(self, exclude=None):
        if 'slug' in exclude:
            exclude.remove('slug')
        try:
            super(Topic, self).validate_unique(exclude)
        except ValidationError as e:
            if ('slug' in e.message_dict and 
                u'Topic with this Slug already exists.' in e.message_dict['slug']):
                e.message_dict['slug'].remove(
                    u'Topic with this Slug already exists.')
                if len(e.message_dict['slug']) == 0:
                    del e.message_dict['slug']
                if not ('preferred_name' in e.message_dict and
                        u'Topic with this Preferred name already exists.' in e.message_dict['preferred_name']):
                    if not 'preferred_name' in e.message_dict:
                        e.message_dict['preferred_name'] = []
                    e.message_dict['preferred_name'].append(u'Topic with a very similar Preferred name already exists.')
            raise e
    class Meta:
        ordering = ['slug']


class Note(LastUpdateMetadata, Administered, URLAccessible):
    u""" 
    Text written by an editor or curator. The text is stored as XHTML,
    so it may have hyperlinks and all the other features that XHTML
    enables.
    """
    title = models.CharField(max_length='80', unique=True)
    content = fields.XHTMLField()
    topics = generic.GenericRelation('TopicAssignment')
    citations = generic.GenericRelation('Citation')
    def has_topic(self, topic):
        return topic.id in self.topics.values_list('topic_id', flat=True)
    def as_text(self):
        return self.title
    class Meta:
        ordering = ['-last_updated']  

class UserProfile(models.Model, URLAccessible):
    user = models.ForeignKey(User, unique=True)
    def _get_display_name(self):
        "Returns the full name if available, or the username if not."
        display_name = self.user.username
        if self.user.first_name:
            display_name = self.user.first_name
            if self.user.last_name:
                display_name = '%s %s' % (self.user.first_name, self.user.last_name)
        return display_name
    display_name = property(_get_display_name)
    @models.permalink
    def get_absolute_url(self):
        return ('user_view', [str(self.user.username)])
    def as_text(self):
        return self.display_name
    @staticmethod
    def get_for(user):
        try:
            return user.get_profile()
        except UserProfile.DoesNotExist:
            return UserProfile.objects.create(user=user)

# -------------------------------------------------------------------------------
# Support models.
# -------------------------------------------------------------------------------

class Alias(CreationMetadata):
    u"""
    An alternate name for a topic.
    """
    topic = models.ForeignKey(Topic, related_name='aliases')
    name = models.CharField(max_length='80')
    def __unicode__(self):
        return self.name
    class Meta(CreationMetadata.Meta):
        unique_together = ('topic', 'name')
        verbose_name_plural = 'aliases'

class TopicAssignment(CreationMetadata):
    u""" 
    An assignment of a topic to any other object.
    """
    topic = models.ForeignKey(Topic, related_name='assignments')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    def __unicode__(self):
        return self.topic.preferred_name
    class Meta(CreationMetadata.Meta):
        unique_together = ('topic', 'object_id')

class Scan(CreationMetadata):
    u"""
    A scanned image associated with a source.
    """
    source = models.ForeignKey(Source, related_name='scans')
    image = models.ImageField(upload_to='scans/%Y/%m')
    ordering = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return u'Scan for %s (order: %s)' % (self.source, self.ordering)
    class Meta:
        ordering = ['ordering'] 

class Citation(CreationMetadata):
    u"""
    A reference to or citation of a documented source.
    """
    source = models.ForeignKey(Source, related_name='citations')
    locator = models.CharField(max_length=16, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
