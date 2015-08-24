# -*- coding: utf-8 -*-

from io import BytesIO
import json
import os
import re
from hashlib import md5
from itertools import chain
import unicodedata

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.utils.html import escape, strip_tags, strip_entities
from django.utils.safestring import mark_safe
from lxml import etree, html
from PIL import Image
import reversion

from editorsnotes.auth.models import ProjectPermissionsMixin, UpdatersMixin
from editorsnotes.djotero.models import ZoteroItem

from .. import fields, utils
from base import (CreationMetadata, LastUpdateMetadata, URLAccessible,
                  Administered, OrderingManager)

__all__ = ['Document', 'Transcript', 'Footnote', 'Scan', 'DocumentLink',
           'Citation']

class DocumentManager(models.Manager):
    use_for_related_fields = True
    # Include whether or not documents have scans/transcripts in default query.
    def get_queryset(self):
        return super(DocumentManager, self).get_queryset()\
            .select_related('_transcript', 'zotero_link', 'project')\
            .extra(select = { 'link_count': '''SELECT COUNT(*) 
FROM main_documentlink WHERE main_documentlink.document_id = main_document.id''',
                              'scan_count': '''SELECT COUNT(*) 
FROM main_scan WHERE main_scan.document_id = main_document.id''',
                              'part_count': '''SELECT COUNT(*) 
FROM main_document AS part WHERE part.collection_id = main_document.id''',
                              '_has_transcript': '''EXISTS ( SELECT 1 
FROM main_transcript WHERE main_transcript.document_id = main_document.id )''' })


class Document(LastUpdateMetadata, Administered, URLAccessible, 
               ProjectPermissionsMixin, UpdatersMixin, ZoteroItem):
    u"""
    Anything that can be taken as evidence for (documentation of) something.

    Documents are best defined by example: letters, newspaper articles, 
    contracts, photographs, database records, whole databases, etc. etc.
    Note that a document may be a collection of other documents.
    """
    import_id = models.CharField(max_length=64, editable=False, 
                                 blank=True, null=True, 
                                 unique=True, db_index=True)
    project = models.ForeignKey('Project', related_name='documents')
    description = fields.XHTMLField()
    description_digest = models.CharField(max_length=32, editable=False)
    collection = models.ForeignKey('self', related_name='parts', blank=True, null=True)
    ordering = models.CharField(max_length=32, editable=False)
    language = models.CharField(max_length=32, default='English')
    related_topics = GenericRelation('TopicAssignment')
    objects = DocumentManager()
    edtf_date = models.TextField(blank=True, null=True)
    class Meta:
        app_label = 'main'
        ordering = ['ordering','import_id']    
        unique_together = ('project', 'description_digest')
    def as_text(self):
        return utils.xhtml_to_text(self.description)
    @staticmethod
    def strip_description(description):
        description_str = etree.tostring(description) \
                if isinstance(description, html.HtmlElement) \
                else description
        return ''.join(
            char for char in strip_entities(strip_tags(description_str))
            if unicodedata.category(char)[0] in 'LNZ')
    @staticmethod
    def hash_description(description):
        string_to_hash = Document.strip_description(description).lower()
        return md5(string_to_hash).hexdigest()
    def validate_unique(self, exclude=None):
        super(Document, self).validate_unique(exclude)
        qs = self.__class__.objects.filter(
            description_digest=Document.hash_description(self.description),
            project_id=self.project.id)
        if self.id:
            qs = qs.exclude(id=self.id)
        if qs.exists():
            raise ValidationError({
                'description': [u'Document with this description already exists.']
            })
    @models.permalink
    def get_absolute_url(self):
        return ('api:documents-detail', [str(self.project.slug), str(self.id)])
    def get_affiliation(self):
        return self.project
    @property
    def transcript(self):
        try:
            return self._transcript
        except Transcript.DoesNotExist:
            return None
    def get_link_count(self):
        if hasattr(self, 'link_count'):
            return self.link_count
        return self.links.count()
    def has_links(self):
        return self.get_link_count() > 0
    def get_scan_count(self):
        if hasattr(self, 'scan_count'):
            return self.scan_count
        return self.scans.count()
    def has_scans(self):
        return self.get_scan_count() > 0
    def get_part_count(self):
        if hasattr(self, 'part_count'):
            return self.part_count
        return self.parts.count()
    def has_parts(self):
        return self.get_part_count() > 0
    def has_transcript(self):
        if hasattr(self, '_has_transcript'):
            return self._has_transcript
        return self.transcript is not None
    def get_all_representations(self):
        r = []
        if self.has_transcript():
            r.append('Transcript')
        if self.has_scans():
            r.append('Scans')
        if hasattr(self, 'link_count') and self.link_count:
            r.append('External Link')
        return r
    def get_all_related_topics(self):
        topic_ct = ContentType.objects.get_by_natural_key(
            'main', 'topic')
        topic_citations = self.citations.filter(content_type_id=topic_ct.id)
        citation_note_sections = self.citationns_set.all()
        notes = {ns.note for ns in citation_note_sections}

        return {ta.topic for ta in set(chain(
            # Explicitly related topics
            self.related_topics.all(),

            # The topic of any TopicSummary objects citing this doc
            [cite.content_object for cite in topic_citations],

            # The related topics of the topic gotten previously
            chain(*[cite.content_object.assignments.all()
                   for cite in topic_citations]),

            # Topics related to sections citing to this doc
            chain(*[sec.related_topics.all() for sec in citation_note_sections]),

            # Topics relate to the note citing this doc
            chain(*[n.related_topics.all() for n in notes])
        ))}

    # FIXME
    def get_citations(self):
        #from editorsnotes.main.models import CitationNS
        from editorsnotes.main.models import Citation

        #note_sections = CitationNS.objects.filter(document_id=self.id)
        citations = Citation.objects.filter(document_id=self.id)

        return sorted(chain(citations), key=lambda obj: obj.last_updated)

    def as_html(self):
        if self.zotero_data is not None:
            data_attributes = ''.join(
                [ ' data-%s="%s"' % (k, escape(v)) 
                  for k, v in self.get_zotero_fields() if v and k not in ['tags', 'extra'] ])
        else:
            data_attributes = ''
        if self.edtf_date:
            data_attributes += ' data-edtf-date="%s"' % self.edtf_date
        data_attributes += ' data-representations="%s"' % (
            self.get_all_representations()) if self.get_all_representations() else ''
        return mark_safe(
            '<div id="document-%s" class="document%s"%s>%s</div>' % (
                self.id,
                (self.has_transcript() or self.has_scans()) 
                 and ' has-scans-or-transcript' or '',
                data_attributes,
                etree.tostring(self.description)))
    def save(self, *args, **kwargs):
        self.ordering = re.sub(r'[^\w\s]', '', utils.xhtml_to_text(self.description))[:32]
        self.description_digest = Document.hash_description(self.description)
        return super(Document, self).save(*args, **kwargs)
reversion.register(Document)

class TranscriptManager(models.Manager):
    # Include related document in default query.
    def get_queryset(self):
        return super(TranscriptManager, self).get_queryset()\
            .select_related('document')

class Transcript(LastUpdateMetadata, Administered, URLAccessible, ProjectPermissionsMixin):
    u"""
    A text transcript of a document.
    """
    document = models.OneToOneField(Document, related_name='_transcript')
    content = fields.XHTMLField()
    objects = TranscriptManager()
    class Meta:
        app_label = 'main'
    def as_text(self):
        return self.document.as_text()
    def get_affiliation(self):
        return self.document.project
    def get_absolute_url(self):
        # Transcripts don't have their own URLs; use the document URL.
        return '%s#transcript' % self.document.get_absolute_url()
    def get_admin_url(self):
        return reverse('admin:main_transcript_add_or_change',
                       args=(self.document_id,))
    def as_html(self):
        return self.document.as_html()
    def get_footnote_href_ids(self):
        anchors = (self.content.cssselect('a.footnote') 
                   if self.content is not None else [])
        return [int(re.findall('\d+', a.attrib.get('href'))[0]) for a in anchors]
    def get_footnotes(self):
        fn_ids = self.get_footnote_href_ids()
        return sorted(self.footnotes.all(),
                      key=lambda fn: fn_ids.index(fn.id)
                      if fn.id in fn_ids else 9999)
reversion.register(Transcript)

class Footnote(LastUpdateMetadata, Administered, URLAccessible,
               ProjectPermissionsMixin):
    u"""
    A footnote attached to a transcript.
    """
    transcript = models.ForeignKey(Transcript, related_name='footnotes')
    content = fields.XHTMLField()
    class Meta:
        app_label = 'main'
    def get_affiliation(self):
        return self.transcript.document.project
    @models.permalink
    def get_absolute_url(self):
        document = self.transcript.document
        return ('footnote_view', [document.project.slug, document.id, self.id])
    def footnoted_text(self):
        try:
            selector = 'a.footnote[href="%s"]' % self.get_absolute_url()
            results = self.transcript.content.cssselect(selector)
            if len(results) == 1:
                return unicode(results[0].xpath('string()'))
        except NoReverseMatch: # footnote has been deleted
            pass
        return None 
    def as_text(self):
        footnoted_text = self.footnoted_text()
        if footnoted_text is None:
            return utils.xhtml_to_text(self.content)
        else:
            return footnoted_text
    def remove_self_from(self, transcript):
        selector = 'a.footnote[href="%s"]' % self.get_absolute_url()
        results = transcript.content.cssselect(selector)
        if len(results) == 1:
            results[0].drop_tag()
    def delete(self, *args, **kwargs):
        self.remove_self_from(self.transcript)
        self.transcript.save()
        super(Footnote, self).delete(*args, **kwargs)
reversion.register(Footnote)

class Scan(CreationMetadata, ProjectPermissionsMixin):
    u"""
    A scanned image of (part of) a document.
    """
    document = models.ForeignKey(Document, related_name='scans')
    image = models.ImageField(upload_to='scans/%Y/%m')
    image_thumbnail = models.ImageField(upload_to='scans/%Y/%m', blank=True, null=True)
    ordering = models.IntegerField(blank=True, null=True)
    objects = OrderingManager()
    class Meta:
        app_label = 'main'
        ordering = ['ordering', '-created'] 
    def __unicode__(self):
        return u'Scan for %s (order: %s)' % (self.document, self.ordering)
    def generate_thumbnail(self, save=True):
        size = 256, 256

        self.image.seek(0)
        thumbnail_image = Image.open(self.image)
        thumbnail_image.thumbnail(size, Image.ANTIALIAS)

        thumbfile = BytesIO()
        thumbnail_image.save(thumbfile, format=thumbnail_image.format)
        thumbfile.seek(0)

        path, ext = os.path.splitext(self.image.name)
        thumbnail_name = os.path.join(path + '_thumb', ext)
        self.image_thumbnail.save(path + '_thumb' + ext,
                                  ContentFile(thumbfile.read()),
                                  save=save)
        thumbfile.close()

    def save(self, *args, **kwargs):
        if self.image and not self.pk:
            self.generate_thumbnail(save=False)
        return super(Scan, self).save(*args, **kwargs)

reversion.register(Scan)

class DocumentLink(CreationMetadata):
    u"""
    A link to an online version of or catalog entry for a document.
    """
    document = models.ForeignKey(Document, related_name='links')
    url = models.URLField()
    description = models.TextField(blank=True)
    class Meta:
        app_label = 'main'
    def __unicode__(self):
        return self.url
reversion.register(DocumentLink)

class DocumentMetadata(CreationMetadata):
    u"""
    Aribitrary metadata (key-value pair) for a document.
    """
    document = models.ForeignKey(Document, related_name='metadata')
    key = models.CharField(max_length=32)
    value = models.TextField()
    class Meta:
        app_label = 'main'
        unique_together = ('document', 'key')

class CitationManager(OrderingManager):
    def get_for_object(self, obj):
        return self.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id)

class Citation(LastUpdateMetadata, ProjectPermissionsMixin):
    u"""
    A reference to or citation of a document.
    """
    document = models.ForeignKey(Document, related_name='citations')
    ordering = models.IntegerField(blank=True, null=True)
    notes = fields.XHTMLField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = CitationManager()

    class Meta:
        app_label = 'main'
        ordering = ['ordering']

    def has_notes(self):
        return self.notes is not None
    def __unicode__(self):
        return u'Citation for %s (order: %s)' % (self.document, self.ordering)
    def get_affiliation(self):
        return self.document.project
