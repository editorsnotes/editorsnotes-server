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

class CreationMetadata(models.Model):
    creator = models.ForeignKey(User, editable=False, related_name='created_%(class)s_set')
    created = models.DateTimeField(auto_now_add=True)
    def created_display(self):
        return utils.timeago(self.created)
    created_display.allow_tags = True
    created_display.short_description = 'created'
    created_display.admin_order_field = 'created'
    def creator_display(self):
        return UserProfile.get_for(self.creator).name_display()
    creator_display.allow_tags = True
    def edit_history(self):
        return u'Created by %s %s.' % (
            self.creator_display(), self.created_display())
    edit_history.allow_tags = True
    class Meta:
        abstract = True
        get_latest_by = 'created'

class LastUpdateMetadata(CreationMetadata):
    last_updater = models.ForeignKey(User, editable=False, related_name='last_to_update_%(class)s_set')
    last_updated = models.DateTimeField(auto_now=True)    
    def last_updated_display(self):
        return utils.timeago(self.last_updated)
    last_updated_display.allow_tags = True
    last_updated_display.short_description = 'last updated'
    last_updated_display.admin_order_field = 'last_updated'
    def last_updater_display(self):
        return UserProfile.get_for(self.last_updater).name_display()
    last_updater_display.allow_tags = True
    def edit_history(self):
        return u'Created by %s %s.<br/>Last edited by %s %s.' % (
            self.creator_display(), self.created_display(),
            self.last_updater_display(), self.last_updated_display())
    edit_history.allow_tags = True
    class Meta:
        abstract = True

class Topic(LastUpdateMetadata):
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
    def summary_as_html(self):
        return etree.tostring(self.summary)
    def summary_as_text(self):
        return utils.xhtml_to_text(self.summary)    
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
    def __unicode__(self):
        return unicode(self.preferred_name)
    def get_aliases(self):
        return u' '.join([ a.name for a in self.aliases.all() ])
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
            
    #@models.permalink
    def get_absolute_url(self):
        return '/topic/%s/' % self.slug
        #return ('topic_view', (), { 'slug': self.slug })
    def get_admin_url(self):
        return urlresolvers.reverse('admin:main_topic_change', args=(self.id,))
    class Meta:
        ordering = ['preferred_name']

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
    An assignment of a topic to a note.
    """
    topic = models.ForeignKey(Topic, related_name='assignments')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    def __unicode__(self):
        return self.topic.preferred_name
    class Meta(CreationMetadata.Meta):
        unique_together = ('topic', 'object_id')

class Note(LastUpdateMetadata):
    u""" 
    Text written by an editor or curator. The text is stored as XHTML,
    so it may have hyperlinks and all the other features that XHTML
    enables.
    """
    content = fields.XHTMLField()
    topics = generic.GenericRelation('TopicAssignment')
    citations = generic.GenericRelation('Citation')
    def has_topic(self, topic):
        return topic.id in self.topics.values_list('topic_id', flat=True)
    def content_as_html(self):
        return etree.tostring(self.content)
    def content_as_text(self):
        return utils.xhtml_to_text(self.content)
    def excerpt(self):
        return utils.truncate(utils.xhtml_to_text(self.content))
    def __unicode__(self):
        return self.excerpt()
    def get_absolute_url(self):
        return '/note/%s/' % self.id
    def get_admin_url(self):
        return urlresolvers.reverse('admin:main_note_change', args=(self.id,))
    class Meta:
        ordering = ['-last_updated']  

class Source(CreationMetadata):
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
    # For search indexing.
    def transcript_and_footnotes_as_text(self):
        try:
            html = self._transcript.content_as_html()
            for f in self._transcript.footnotes.all():
                html += ' ' + f.content_as_html()
            return html
        except Transcript.DoesNotExist:
            return ''
    def description_as_text(self):
        return utils.xhtml_to_text(self.description)
    def description_as_html(self):
        e = deepcopy(self.description)
        if self.url:
            a = etree.SubElement(e, 'a')
            a.attrib['href'] = self.url
            a.text = self.url
            utils.prepend_space(a)
        if self.transcript:
            a = etree.SubElement(e, 'a')
            a.attrib['href'] = self.transcript.get_absolute_url()
            a.text = 'View transcript'
            utils.prepend_space(a)
        return etree.tostring(e)
    def save(self, *args, **kwargs):
        self.ordering = re.sub(r'[^\w\s]', '', utils.xhtml_to_text(self.description))[:32]
        super(Source, self).save(*args, **kwargs)
    def __unicode__(self):
        return utils.truncate(self.description_as_text())
    def get_absolute_url(self):
        return '/source/%s/' % self.id
    class Meta:
        ordering = ['ordering']    

class Scan(CreationMetadata):
    u"""
    A scanned image associated with a source.
    """
    source = models.ForeignKey(Source, related_name='scans')
    image = models.ImageField(upload_to='scans/%Y/%m')
    ordering = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return self.image.url
    class Meta:
        ordering = ['ordering'] 

class Transcript(CreationMetadata):
    u"""
    A text transcript of a primary source document.
    """
    source = models.OneToOneField(Source, related_name='_transcript')
    content = fields.XHTMLField()
    def content_as_html(self):
        return etree.tostring(self.content)
    def content_as_text(self):
        return utils.xhtml_to_text(self.content)
    def get_absolute_url(self):
        return '/transcript/%s/' % self.id
    def __unicode__(self):
        return u'Transcript of %s' % self.source

class Footnote(CreationMetadata):
    u"""
    A footnote attached to a transcript.
    """
    transcript = models.ForeignKey(Transcript, related_name='footnotes')
    content = fields.XHTMLField()
    def content_as_html(self):
        return etree.tostring(self.content)
    def get_absolute_url(self):
        return '/footnote/%s/' % self.id
    def delete(self, *args, **kwargs):
        selector = 'a.footnote[href="%s"]' % self.get_absolute_url()
        results = self.transcript.content.cssselect(selector)
        if len(results) == 1:
            a = results[0]
            for element in a: a.addprevious(element)
            a.drop_tree()
        super(Footnote, self).delete(*args, **kwargs)
    def __unicode__(self):
        return utils.truncate(utils.xhtml_to_text(self.content))

class Citation(CreationMetadata):
    u"""
    A reference to or citation of a documented source.
    """
    source = models.ForeignKey(Source, related_name='citations')
    locator = models.CharField(max_length=16, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    def as_html(self):
        e = deepcopy(self.source.description)
        if self.locator:
            s = etree.SubElement(e, 'span')
            s.text = self.locator + '.'
            utils.prepend_space(s)
        if self.source.url:
            a = etree.SubElement(e, 'a')
            a.attrib['href'] = self.source.url
            a.text = self.source.url
            utils.prepend_space(a)
        if self.source.transcript:
            a = etree.SubElement(e, 'a')
            a.attrib['href'] = self.source.transcript.get_absolute_url()
            a.text = 'View transcript'
            utils.prepend_space(a)
        return etree.tostring(e)

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    def get_absolute_url(self):
        return '/user/%s/' % self.user.username
    def _get_display_name(self):
        "Returns the full name if available, or the username if not."
        display_name = self.user.username
        if self.user.first_name:
            display_name = self.user.first_name
            if self.user.last_name:
                display_name = '%s %s' % (self.user.first_name, self.user.last_name)
        return display_name
    display_name = property(_get_display_name)
    def last_login_display(self):
        return utils.timeago(self.user.last_login)
    last_login_display.allow_tags = True
    def name_display(self):
        return '<a class="quiet subtle" href="%s">%s</a>' % (self.get_absolute_url(), self.display_name)
    name_display.allow_tags = True
    @staticmethod
    def get_for(user):
        try:
            return user.get_profile()
        except UserProfile.DoesNotExist:
            return UserProfile.objects.create(user=user)



