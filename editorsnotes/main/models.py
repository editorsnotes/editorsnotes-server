from django.db import models
from django.contrib.auth.models import User
from lxml import etree

class ElementField(models.Field):
    description = 'A parsed XML document or fragment'
    __metaclass__ = models.SubfieldBase
    def __init__(self, *args, **kwargs):
        super(ElementField, self).__init__(*args, **kwargs)
    def db_type(self):
        return 'xml'
    def to_python(self, value):
        if isinstance(value, etree._Element):
            return value
        return etree.fromstring(value)
    def get_db_prep_value(self, value):
        return etree.tostring(value)
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(ElementField, self).formfield(**defaults)

class Metadata(models.Model):
    creator = models.ForeignKey(User, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    class Meta:
        abstract = True
        get_latest_by = 'created'

class Note(Metadata):
    u""" 
    Text written by an editor or curator. The text is stored as XHTML,
    so it may have hyperlinks and all the other features that XHTML
    enables.

    'is_query' indicates whether the note is asking something rather
    than or explaining or describing something.

    >>> user = User.objects.create_user('tester', '', 'testerpass')
    >>> note = Note.objects.create(content=u'<p>This is a note.</p>', creator=user)
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
    content = ElementField()
    is_query = models.BooleanField(default=False)
    terms = models.ManyToManyField('Term', through='TermAssignment')

class Reference(Metadata):
    u"""
    A bibliographic citation (as XHTML) and reference to a document.
    """
    note = models.ForeignKey(Note, related_name='references', editable=False)
    citation = ElementField()
    url = models.URLField(blank=True, verify_exists=True)
    class Meta(Metadata.Meta):
        unique_together = ('note', 'url')

class Term(Metadata):
    u""" 
    A controlled term such as a person name, an organization name, a
    place name, an event name, a publication name, or the name of a
    topic or theme.
    """
    preferred_name = models.CharField(max_length='80', unique=True)
    def __unicode__(self):
        return self.preferred_name

class Alias(Metadata):
    u"""
    An alternate name for a term.
    """
    term = models.ForeignKey(Term, related_name='aliases', editable=False)
    name = models.CharField(max_length='80')
    def __unicode__(self):
        return self.name
    class Meta(Metadata.Meta):
        unique_together = ('term', 'name')
        verbose_name_plural = 'aliases'

class TermAssignment(Metadata):
    u""" 
    An assignment of a term to a note.
    """
    term = models.ForeignKey(Term, related_name='terms', editable=False)
    note = models.ForeignKey(Note, related_name='notes', editable=False)
    def __unicode__(self):
        return self.term.preferred_name
    class Meta(Metadata.Meta):
        unique_together = ('term', 'note')
