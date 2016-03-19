# -*- coding: utf-8 -*-

import json
import unittest

from django.test import TestCase

from lxml import etree, html

from editorsnotes.auth.models import Project

from .. import models as main_models
from .. import utils


class UtilsTestCase(unittest.TestCase):
    def test_truncate(self):
        self.assertEquals(utils.truncate(u'xxxxxxxxxx', 4), u'xx... xx')

    def test_native_to_utc(self):
        from datetime import datetime
        naive_datetime = datetime(2011, 2, 10, 16, 42, 54, 421353)
        self.assertEquals(  # assuming settings.TIME_ZONE is Pacific Time
            'datetime.datetime(2011, 2, 11, 0, 42, 54, 421353, tzinfo=<UTC>)',
            repr(utils.naive_to_utc(naive_datetime)))
        self.assertEquals(
            'datetime.datetime(2011, 2, 10, 16, 42, 54, 421353, tzinfo=<UTC>)',
            repr(utils.naive_to_utc(naive_datetime, 'UTC')))
        aware_datetime = utils.naive_to_utc(naive_datetime)
        self.assertRaises(TypeError, utils.naive_to_utc, aware_datetime)

    def test_alpha_columns(self):
        import string
        import random

        class Item:
            def __init__(self, key):
                self.key = key

        items = [Item(letter) for letter in string.lowercase]
        random.shuffle(items)
        columns = utils.alpha_columns(items, 'key', itemkey='thing')
        self.assertEquals(3, len(columns))
        self.assertEquals(9, len(columns[0]))
        self.assertEquals(9, len(columns[1]))
        self.assertEquals(8, len(columns[2]))
        self.assertEquals('A', columns[0][0]['first_letter'])
        self.assertEquals('a', columns[0][0]['thing'].key)
        self.assertEquals('J', columns[1][0]['first_letter'])
        self.assertEquals('S', columns[2][0]['first_letter'])
        self.assertEquals('Z', columns[2][7]['first_letter'])

    def test_description_digest(self):
        _hash = main_models.Document.hash_description
        self.assertEqual(
            _hash(u'Prison Memoirs of an Anarchist'),
            _hash(u'<div>Prison Memoirs of an Anarchist</div>'))
        self.assertEqual(
            _hash(u'Prison Memoirs of an Anarchist'),
            _hash(html.fragment_fromstring(
                u'<div>Prison Memoirs of an Anarchist</div>')))
        self.assertEqual(
            _hash(u'Prison Memoirs of an Anarchist'),
            _hash(u'Prison Memoirs of an Anarchist&nbsp;'))
        self.assertEqual(
            _hash(u'Prison Memoirs of an Anarchist'),
            _hash(u'Prison Memoirs of an Anarchist.'))
        self.assertEqual(
            _hash(u'Prison Memoirs of an Anarchist'),
            _hash(u'prison memoirs of an anarchist'))

    def test_stray_br_stripped(self):
        "<br/> tags with nothing after them should be removed."
        test1 = html.fragment_fromstring(
            '<div>I am an annoying browser<br/></div>')
        utils.remove_stray_brs(test1)
        self.assertEqual('<div>I am an annoying browser</div>',
                         etree.tostring(test1))

        test2 = html.fragment_fromstring('<div>text<br/>text</div>')
        utils.remove_stray_brs(test2)
        self.assertEqual('<div>text<br/>text</div>', etree.tostring(test2))

        test3 = html.fragment_fromstring(
            '<div>I<br/><br/> am really annoying.<br/><br/><br/></div>')
        utils.remove_stray_brs(test3)
        self.assertEqual('<div>I<br/> am really annoying.</div>',
                         etree.tostring(test3))

        test4 = html.fragment_fromstring('<div><br/>No leading break?</div>')
        utils.remove_stray_brs(test4)
        self.assertEqual('<div>No leading break?</div>', etree.tostring(test4))

    def test_remove_empty_els(self):
        """
        Elements which have no text (or children with text) should be removed,
        with the exception of <br/> and <hr/> tags, or a list of tags provided.
        """

        test1 = html.fragment_fromstring('<div><p></p>just me<hr/></div>')
        utils.remove_empty_els(test1)
        self.assertEqual('<div>just me<hr/></div>', etree.tostring(test1))

        test2 = html.fragment_fromstring(
            '<div><div>a</div>bcd<div><b></b></div>e</div>')
        utils.remove_empty_els(test2)
        self.assertEqual('<div><div>a</div>bcde</div>', etree.tostring(test2))

        test3 = html.fragment_fromstring('<div><p></p><hr/></div>')
        utils.remove_empty_els(test3, ignore=('p',))
        self.assertEqual('<div><p/></div>', etree.tostring(test3))


class MarkupUtilsTestCase(TestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.project = Project.objects.get(slug='emma')
        self.user = self.project.members.all()[0]

    def test_render_markup(self):
        from ..utils import markup

        html = markup.render_markup('test', self.project)
        self.assertEqual(etree.tostring(html), u'<div><p>test</p></div>')

    def test_count_references(self):
        from ..utils import markup, markup_html

        document = main_models.Document.objects.create(
            description='Ryan Shaw, <em>My Big Book of Cool Stuff</em>, 2010.',
            zotero_data=json.dumps({
                'itemType': 'book',
                'title': 'My Big Book of Cool Stuff',
                'creators': [
                    {
                        'creatorType': 'author',
                        'firstName': 'Ryan',
                        'lastName': 'Shaw'
                    }
                ],
                'date': '2010'
            }),
            creator=self.user, last_updater=self.user, project=self.project)

        html = markup.render_markup(u'I am citing [@@d{}]'.format(document.id),
                                    self.project)
        self.assertEqual(etree.tostring(html), (
            u'<div><p>I am citing <cite>('
            '<a href="/projects/emma/documents/{}/" '
            'class="ENInlineReference ENInlineReference-document">'
            'Shaw 2010'
            '</a>)</cite></p></div>'.format(document.id)
        ))

        related_items = markup_html.get_embedded_models(html)
        self.assertEqual(len(related_items['document']), 1)

    def test_render_topic_reference(self):
        from ..utils import markup, markup_html

        topic = main_models.Topic.objects.create(
            preferred_name='Ryan Shaw',
            creator=self.user, last_updater=self.user, project=self.project)

        html = markup.render_markup(u'This is about @@t{}.'.format(topic.id),
                                    self.project)
        self.assertEqual(etree.tostring(html), (
            u'<div><p>This is about '
            '<a href="/projects/emma/topics/{}/" '
            'class="ENInlineReference ENInlineReference-topic">'
            'Ryan Shaw'
            '</a>.</p></div>'.format(topic.id)
        ))

        related_items = markup_html.get_embedded_models(html)
        self.assertEqual(len(related_items['topic']), 1)
