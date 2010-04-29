# -*- coding: utf-8 -*-

import re
import os.path
from lxml import etree, html
from unaccent import unaccent
from isodate import datetime_isoformat
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode

textify = etree.XSLT(etree.parse(
        os.path.abspath(os.path.join(os.path.dirname(__file__), 'textify.xsl'))))

def xhtml_to_text(xhtml):
    return etree.tostring(textify(xhtml), method='text', encoding=unicode).strip()

def truncate(text, length=100):
    u"""
    >>> truncate(u'xxxxxxxxxx', 4)
    u'xx... xx'
    """
    if len(text) <= length:
        return text
    l = text[:(length/2)].rsplit(' ', 1)[0]
    r = text[-(length/2):].split(' ', 1)
    if len(r) == 1:
        r = r[0]
    else:
        r = r[1]
    return l + u'... ' + r

class XHTMLWidget(forms.Textarea):
    def _format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, html.HtmlElement):
            return etree.tostring(value)
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TypeError('%s cannot be formatted as XHTML' % value)
 
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<textarea%s>%s</textarea>' % (
                forms.util.flatatt(final_attrs),
                conditional_escape(force_unicode(self._format_value(value)))))


class XHTMLField(models.Field):
    description = 'A parsed XHTML fragment'
    __metaclass__ = models.SubfieldBase
    def __init__(self, *args, **kwargs):
        super(XHTMLField, self).__init__(*args, **kwargs)
    def db_type(self):
        return 'xml'
    def to_python(self, value):
        if isinstance(value, html.HtmlElement):
            return value
        if not (isinstance(value, str) or isinstance(value, unicode)):
            raise TypeError('%s cannot be parsed to XHTML' % type(value))
        if len(value) == 0:
            return None
        try:
            return html.fragment_fromstring(value)
        except etree.ParserError:
            return html.fragment_fromstring(value, create_parent='div')
    def get_db_prep_value(self, value):
        return etree.tostring(value)
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
    def formfield(self, **kwargs):
        defaults = {'widget': XHTMLWidget}
        defaults.update(kwargs)
        return super(XHTMLField, self).formfield(**defaults)

class CreationMetadata(models.Model):
    creator = models.ForeignKey(User, editable=False, related_name='created_%(class)s_set')
    created = models.DateTimeField(auto_now_add=True)
    def created_display(self):
        return u'<time class="timeago" datetime="%s">%s</time>' % (
            datetime_isoformat(self.created), self.created.strftime('%I:%M%p, %b %d %Y'))
    created_display.allow_tags = True
    created_display.short_description = 'created'
    created_display.admin_order_field = 'created'
    class Meta:
        abstract = True
        get_latest_by = 'created'

class Note(CreationMetadata):
    u""" 
    Text written by an editor or curator. The text is stored as XHTML,
    so it may have hyperlinks and all the other features that XHTML
    enables.

    'type' indicates whether this is a 'query' (asking something) or a
    'note' (explaining or describing something).

    Style elements are stripped from content.
    >>> user = User.objects.create_user('tester', '', 'testerpass')
    >>> note = Note.objects.create(content=u'<style>garbage</style><h1>hey</h1><p>this is a <em>note</em></p>', creator=user, last_updater=user)
    >>> note.content_as_html()
    '<div><h1>hey</h1><p>this is a <em>note</em></p></div>'
    >>> note.type
    u'N'

    Add references.
    >>> note.references.create(citation='<p><span class="title">Anarchism and other essays</span>, 3rd edition, 1917</p>', url='http://books.google.com/books?id=U5ZYAAAAMAAJ', creator=user)
    <Reference: Reference object>

    Assign terms.
    >>> term = Term.objects.create(preferred_name=u'Example', creator=user)
    >>> TermAssignment.objects.create(note=note, term=term, creator=user)
    <TermAssignment: Example>
    >>> note.terms.all()
    [<Term: Example>]
    >>> term.note_set.all()
    [<Note: hey this is a note>]
    
    Can't assign the same term more than once.
    >>> TermAssignment.objects.create(note=note, term=term, creator=user)
    Traceback (most recent call last):
    IntegrityError: duplicate key value violates unique constraint "main_termassignment_term_id_key"
    <BLANKLINE>
    """
    content = XHTMLField()
    type = models.CharField(max_length=1, choices=(('N','note'),('Q','query')), default='N')
    terms = models.ManyToManyField('Term', through='TermAssignment')
    last_updater = models.ForeignKey(User, editable=False, related_name='last_to_update_note_set')
    last_updated = models.DateTimeField(auto_now=True)
    def content_as_html(self):
        return etree.tostring(self.content)
    def last_updated_display(self):
        return '<time class="timeago" datetime="%s">%s</time>' % (
            datetime_isoformat(self.last_updated), self.last_updated.strftime('%I:%M%p, %b %d %Y'))
    last_updated_display.allow_tags = True
    last_updated_display.short_description = 'last updated'
    last_updated_display.admin_order_field = 'last_updated'
    def edit_history(self):
        return u'Created by %s %s. Last edited by %s %s.' % (
            self.creator.username, self.created_display(), 
            self.last_updater.username, self.last_updated_display())
    edit_history.allow_tags = True
    def excerpt(self):
        return truncate(xhtml_to_text(self.content))
    def save(self, *args, **kwargs):
        for e in self.content.iter(tag='style'):
            e.getparent().remove(e)
        super(Note, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.excerpt()

class Reference(CreationMetadata):
    u"""
    A bibliographic citation (as XHTML) and reference to a document.
    """
    note = models.ForeignKey(Note, related_name='references')
    citation = XHTMLField()
    url = models.URLField(blank=True, verify_exists=True)
    def citation_as_html(self):
        return etree.tostring(self.citation)

class Term(CreationMetadata):
    u""" 
    A controlled term such as a person name, an organization name, a
    place name, an event name, a publication name, or the name of a
    topic or theme.

    >>> term = Term(preferred_name=u'Foote, Edward B. (Edward Bliss) 1829-1906')
    >>> term.make_slug()
    u'foote-edward-b-edward-bliss-1829-1906'

    >>> term = Term(preferred_name=u'Räggler å paschaser på våra mål tå en bonne')
    >>> term.make_slug()
    u'raggler-a-paschaser-pa-vara-mal-ta-en-bonne'
    """
    preferred_name = models.CharField(max_length='80', unique=True)
    slug = models.CharField(max_length='80', unique=True, editable=False)
    def make_slug(self):
        return '-'.join(
            [ x for x in re.split('\W+', unaccent(self.__unicode__()))
              if len(x) > 0 ]).lower()
    def save(self, *args, **kwargs):
        self.slug = self.make_slug()
        super(Term, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.preferred_name
    #@models.permalink
    def get_absolute_url(self):
        return '/t/%s/' % self.slug
        #return ('term_view', (), { 'slug': self.slug })

class Alias(CreationMetadata):
    u"""
    An alternate name for a term.
    """
    term = models.ForeignKey(Term, related_name='aliases')
    name = models.CharField(max_length='80')
    def __unicode__(self):
        return self.name
    class Meta(CreationMetadata.Meta):
        unique_together = ('term', 'name')
        verbose_name_plural = 'aliases'

class TermAssignment(CreationMetadata):
    u""" 
    An assignment of a term to a note.
    """
    term = models.ForeignKey(Term)
    note = models.ForeignKey(Note, related_name='notes')
    def __unicode__(self):
        return self.term.preferred_name
    class Meta(CreationMetadata.Meta):
        unique_together = ('term', 'note')
        verbose_name_plural = 'index terms'
