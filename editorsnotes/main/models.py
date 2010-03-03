from lxml import etree, html
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode

class XHTMLWidget(forms.Textarea):
    def _format_value(self, value):
        if value is None:
            return ''
        return etree.tostring(value)
 
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
        return html.fragment_fromstring(value, create_parent=True)
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
    class Meta:
        abstract = True
        get_latest_by = 'created'

class Note(CreationMetadata):
    u""" 
    Text written by an editor or curator. The text is stored as XHTML,
    so it may have hyperlinks and all the other features that XHTML
    enables.

    'is_query' indicates whether the note is asking something rather
    than or explaining or describing something.

    >>> user = User.objects.create_user('tester', '', 'testerpass')
    >>> note = Note.objects.create(content=u'<h1>hey</h1><p>this is a <em>note</em></p>', creator=user, last_updater=user)
    >>> note.is_query
    False

    Add references.
    >>> note.references.create(citation='<p><span class="title">Anarchism and other essays</span>, 3rd edition, 1917</p>', url='http://books.google.com/books?id=U5ZYAAAAMAAJ', creator=user)
    <Reference: Reference object>

    Assign terms.
    >>> term = Term.objects.create(preferred_name=u'Example', creator=user)
    >>> TermAssignment.objects.create(note=note, term=term, creator=user)
    <TermAssignment: Example>
    >>> note.terms.all()
    [<Term: Example>]
    
    Can't assign the same term more than once.
    >>> TermAssignment.objects.create(note=note, term=term, creator=user)
    Traceback (most recent call last):
    IntegrityError: duplicate key value violates unique constraint "main_termassignment_term_id_key"
    <BLANKLINE>
    """
    content = XHTMLField()
    is_query = models.BooleanField(default=False, verbose_name='this is a query')
    terms = models.ManyToManyField('Term', through='TermAssignment')
    last_updater = models.ForeignKey(User, editable=False, related_name='last_to_update_note_set')
    last_updated = models.DateTimeField(auto_now=True)

class Reference(CreationMetadata):
    u"""
    A bibliographic citation (as XHTML) and reference to a document.
    """
    note = models.ForeignKey(Note, related_name='references')
    citation = XHTMLField()
    url = models.URLField(blank=True, verify_exists=True)
    class Meta(CreationMetadata.Meta):
        unique_together = ('note', 'url')

class Term(CreationMetadata):
    u""" 
    A controlled term such as a person name, an organization name, a
    place name, an event name, a publication name, or the name of a
    topic or theme.
    """
    preferred_name = models.CharField(max_length='80', unique=True)
    def __unicode__(self):
        return self.preferred_name

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
    term = models.ForeignKey(Term, related_name='terms')
    note = models.ForeignKey(Note, related_name='notes')
    def __unicode__(self):
        return self.term.preferred_name
    class Meta(CreationMetadata.Meta):
        unique_together = ('term', 'note')
        verbose_name_plural = 'index terms'
