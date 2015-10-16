# -*- coding: utf-8 -*-

import itertools
import numbers

from django.conf import settings
from django.db import models
from django.utils.html import conditional_escape

from editorsnotes.search.items.helpers import get_referencing_items

from .. import fields
from .. import utils
from ..utils.markup import render_markup


class CreationMetadata(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, editable=False,
        related_name='created_%(class)s_set')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        get_latest_by = 'created'


class LastUpdateMetadata(CreationMetadata):
    last_updater = models.ForeignKey(
        settings.AUTH_USER_MODEL, editable=False,
        related_name='last_to_update_%(class)s_set')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ENMarkup(models.Model):
    markup = models.TextField(blank=True, null=True)
    markup_html = fields.XHTMLField(blank=True, null=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.markup:
            self.markup_html = render_markup(self.markup, self.project)
        return super(ENMarkup, self).save(*args, **kwargs)

    def has_markup(self):
        return self.markup_html is not None

    def get_referenced_items(self):
        from ..utils.markup_html import get_embedded_item_urls
        if not self.has_markup():
            return []

        urls_by_type = get_embedded_item_urls(self.markup_html)
        embedded_urls = set(itertools.chain(*urls_by_type.values()))
        return embedded_urls


class Administered(object):
    pass


class URLAccessible(object):
    @models.permalink
    def get_absolute_url(self):
        return ('api:{}s-detail'.format(self._meta.model_name), [str(self.id)])

    def __unicode__(self):
        return utils.truncate(self.as_text())

    def as_text(self):
        raise Exception('Must implement %s.as_text()' % self._meta.model_name)


class IsReferenced(object):
    def get_referencing_items(self, labels=False):
        url = self.get_absolute_url()
        referencing_urls = get_referencing_items(url)

        return referencing_urls
