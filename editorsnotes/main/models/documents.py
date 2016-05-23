# -*- coding: utf-8 -*-

from io import BytesIO
import os
from hashlib import md5
from itertools import chain
import unicodedata

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils.html import strip_tags, strip_entities
from lxml import etree, html
from PIL import Image
from reversion import revisions as reversion

from editorsnotes.auth.models import ProjectPermissionsMixin, UpdatersMixin
from editorsnotes.djotero.models import ZoteroItem

from .. import fields, utils
from .base import (CreationMetadata, LastUpdateMetadata, URLAccessible,
                  Administered, IsReferenced, ENMarkup)

__all__ = ['Document', 'Transcript', 'Scan']


class DocumentManager(models.Manager):
    use_for_related_fields = True
    # Include whether or not documents have scans/transcripts in default query.

    def get_queryset(self):
        return super(DocumentManager, self).get_queryset()\
            .select_related('_transcript', 'zotero_link', 'project')\
            .extra(select={
                'scan_count': '''
SELECT COUNT(*)
FROM main_scan WHERE main_scan.document_id = main_document.id
                ''',

                '_has_transcript': '''
EXISTS ( SELECT 1
FROM main_transcript WHERE main_transcript.document_id = main_document.id )
                '''
            })


class Document(LastUpdateMetadata, Administered, URLAccessible, IsReferenced,
               ProjectPermissionsMixin, UpdatersMixin, ZoteroItem):
    """
    Anything that can be taken as evidence for (documentation of) something.

    Documents are best defined by example: letters, newspaper articles,
    contracts, photographs, database records, whole databases, etc. etc.
    Note that a document may be a collection of other documents.
    """

    project = models.ForeignKey('Project', related_name='documents')

    # FIXME: Should have validation/cleaning
    links = ArrayField(models.CharField(max_length=1000), default=list)

    description = fields.XHTMLField()
    description_digest = models.CharField(max_length=32, editable=False)

    related_topics = GenericRelation('TopicAssignment')

    objects = DocumentManager()

    class Meta:
        app_label = 'main'
        ordering = ['-last_updated']
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
                'description': [
                    'Document with this description already exists.'
                ]
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

    def get_scan_count(self):
        if hasattr(self, 'scan_count'):
            return self.scan_count
        return self.scans.count()

    def has_scans(self):
        return self.get_scan_count() > 0

    def has_transcript(self):
        if hasattr(self, '_has_transcript'):
            return self._has_transcript
        return self.transcript is not None

    # FIXME
    def get_all_related_topics(self):
        # topic_ct = ContentType.objects.get_by_natural_key(
        #     'main', 'topic')
        # topic_citations = self.citations.filter(content_type_id=topic_ct.id)
        # citation_note_sections = self.citationns_set.all()
        # notes = {ns.note for ns in citation_note_sections}

        return {ta.topic for ta in set(chain(
            # Explicitly related topics
            self.related_topics.all(),

            # The topic of any TopicSummary objects citing this doc
            # [cite.content_object for cite in topic_citations],

            # The related topics of the topic gotten previously
            # chain(*[cite.content_object.assignments.all()
            #       for cite in topic_citations]),

            # Topics related to sections citing to this doc
            # chain(*[sec.related_topics.all()
            # for sec in citation_note_sections]),

            # Topics relate to the note citing this doc
            # chain(*[n.related_topics.all() for n in notes])
        ))}

    # FIXME
    def get_citations(self):
        # from editorsnotes.main.models import CitationNS
        # from editorsnotes.main.models import Citation

        # note_sections = CitationNS.objects.filter(document_id=self.id)
        # citations = Citation.objects.filter(document_id=self.id)

        # return sorted(chain(citations), key=lambda obj: obj.last_updated)
        return []

    def save(self, *args, **kwargs):
        self.description_digest = Document.hash_description(self.description)
        return super(Document, self).save(*args, **kwargs)
reversion.register(Document)


class TranscriptManager(models.Manager):
    # Include related document in default query.
    def get_queryset(self):
        return super(TranscriptManager, self)\
            .get_queryset()\
            .select_related('document')


class Transcript(LastUpdateMetadata, Administered, URLAccessible, ENMarkup,
                 ProjectPermissionsMixin):
    """
    A text transcript of a document.
    """
    document = models.OneToOneField(Document, related_name='_transcript')

    objects = TranscriptManager()

    class Meta:
        app_label = 'main'

    def as_text(self):
        return self.document.as_text()

    def get_affiliation(self):
        return self.document.project

    @models.permalink
    def get_absolute_url(self):
        return ('api:transcripts-detail',
                [str(self.document.project.slug), str(self.document_id)])

    # FIXME
    def get_footnotes(self):
        return []
reversion.register(Transcript)


class Scan(CreationMetadata, ProjectPermissionsMixin):
    """
    A scanned image of (part of) a document.
    """
    document = models.ForeignKey(Document, related_name='scans')
    image = models.ImageField(upload_to='scans/%Y/%m')
    image_thumbnail = models.ImageField(upload_to='scans/%Y/%m',
                                        blank=True, null=True)
    ordering = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = 'main'
        ordering = ['ordering', '-created']

    def __unicode__(self):
        return 'Scan for %s (order: %s)' % (self.document, self.ordering)

    def generate_thumbnail(self, save=True):
        size = 256, 256

        self.image.seek(0)
        thumbnail_image = Image.open(self.image)
        thumbnail_image.thumbnail(size, Image.ANTIALIAS)

        thumbfile = BytesIO()
        thumbnail_image.save(thumbfile, format=thumbnail_image.format)
        thumbfile.seek(0)

        path, ext = os.path.splitext(self.image.name)
        self.image_thumbnail.save(path + '_thumb' + ext,
                                  ContentFile(thumbfile.read()),
                                  save=save)
        thumbfile.close()

    def save(self, *args, **kwargs):
        if self.image and not self.pk:
            self.generate_thumbnail(save=False)
        return super(Scan, self).save(*args, **kwargs)
reversion.register(Scan)
