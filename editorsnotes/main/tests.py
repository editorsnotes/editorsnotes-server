# -*- coding: utf-8 -*-

import json
import unittest

from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db import models, transaction, IntegrityError
from django.test import TestCase, TransactionTestCase

from django_nose import FastFixtureTestCase
from lxml import etree, html

from editorsnotes.auth.models import Project, User, ProjectInvitation

import models as main_models
import utils
from views.auth import create_invited_user

class UtilsTestCase(unittest.TestCase):
    def test_truncate(self):
        self.assertEquals(utils.truncate(u'xxxxxxxxxx', 4), u'xx... xx')
    def test_native_to_utc(self):
        from datetime import datetime
        naive_datetime = datetime(2011, 2, 10, 16, 42, 54, 421353)
        self.assertEquals( # assuming settings.TIME_ZONE is Pacific Time
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
        items = [ Item(letter) for letter in string.lowercase ]
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
            _hash(html.fragment_fromstring(u'<div>Prison Memoirs of an Anarchist</div>')))
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
        test1 = html.fragment_fromstring('<div>I am an annoying browser<br/></div>')
        utils.remove_stray_brs(test1)
        self.assertEqual('<div>I am an annoying browser</div>', etree.tostring(test1))

        test2 = html.fragment_fromstring('<div>text<br/>text</div>')
        utils.remove_stray_brs(test2)
        self.assertEqual('<div>text<br/>text</div>', etree.tostring(test2))

        test3 = html.fragment_fromstring('<div>I<br/><br/> am really annoying.<br/><br/><br/></div>')
        utils.remove_stray_brs(test3)
        self.assertEqual('<div>I<br/> am really annoying.</div>', etree.tostring(test3))

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

        test2 = html.fragment_fromstring('<div><div>a</div>bcd<div><b></b></div>e</div>')
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
        from utils import markup

        html = markup.render_markup('test', self.project)
        self.assertEqual(html, u'<p>test</p>\n')

    def test_count_references(self):
        from utils import markup, markup_html

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
        self.assertEqual(html, (
            u'<p>I am citing <cite>('
            '<a rel="http://editorsnotes.org/v#document" '
                'href="/projects/emma/documents/{}/">'
                'Shaw 2010'
            '</a>)</cite></p>\n'.format(document.id)
        ))

        tree = etree.fromstring(html)
        related_documents = markup_html.get_related_documents(tree)
        self.assertEqual(len(related_documents), 1)


def create_test_user():
    user = User(username='testuser', is_staff=True, is_superuser=True)
    user.set_password('testuser')
    user.save()
    return user

class NoteTestCase(TestCase):
    fixtures = ['projects.json']
    def setUp(self):
        self.project = Project.objects.get(slug='emma')
        self.user = self.project.members.all()[0]
    #def testStripStyleElementsFromContent(self):
    #    note = main_models.Note.objects.create(
    #        content=u'<style>garbage</style><h1>hey</h1><p>this is a <em>note</em></p>', 
    #        creator=self.user, last_updater=self.user, project=self.project)
    #    self.assertEquals(
    #        etree.tostring(note.content),
    #        '<div><h1>hey</h1><p>this is a <em>note</em></p></div>')
    #def testAddCitations(self):
    #    document = main_models.Document.objects.create(
    #        description='Ryan Shaw, <em>My Big Book of Cool Stuff</em>, 2010.', 
    #        creator=self.user, last_updater=self.user, project=self.project)

    #    note = main_models.Note.objects.create(
    #        markup=u'I am citing [@@d{}]'.format(document.id),
    #        creator=self.user, last_updater=self.user, project=self.project)

    #    self.assertEquals(note.markup_html,
    #                      '<p>I am citing<span>Shaw 2010</span></p>')

    #    self.assertEquals(note.sections.count(), 1)
    #    self.assertEquals(note.sections_counter, 1)

    def testAssignTopics(self):
        note = main_models.Note.objects.create(
            title='test note',
            markup=u'# hey\n\nthis is a _note_', 
            creator=self.user, last_updater=self.user, project=self.project)
        topic = main_models.Topic.objects.get_or_create_by_name(
            u'Example', self.project, self.user)

        self.assertFalse(note.has_topic(topic))

        note.related_topics.create(topic=topic, creator=self.user)

        self.assertTrue(note.has_topic(topic))
        self.assertEquals(1, len(note.related_topics.all()))
        self.assertEquals(1, len(topic.assignments.all()))
        self.assertEquals(topic, note.related_topics.all()[0].topic)

class DocumentTestCase(TestCase):
    fixtures = ['projects.json']
    def setUp(self):
        self.project = Project.objects.get(slug='emma')
        self.user = self.project.members.all()[0]
        self.document_kwargs = {
            'description': u'<div>My Disillusionment in Russia</div>',
            'project_id': self.project.id,
            'creator_id': self.user.id,
            'last_updater_id': self.user.id
        }
        self.document = main_models.Document.objects.create(**self.document_kwargs)

    def test_hash_description(self):
        self.assertEqual(self.document.description_digest,
                         main_models.Document.hash_description(self.document.description))

    def test_duplicate_descriptions(self):
        data = self.document_kwargs.copy()
        data['description'] = u'“My Disillusionment in Russia”'
        test_document = main_models.Document(**data)
        self.assertRaises(ValidationError, test_document.full_clean)
        self.assertRaises(IntegrityError, test_document.save)

    # TODO: Make sure hashed topic descriptions can be retrieved in
    # elasticsearch

    def test_empty_description(self):
        self.assertRaises(ValidationError,
                          main_models.Document(description='').clean_fields)
        self.assertRaises(ValidationError,
                          main_models.Document(description=' ').clean_fields)
        self.assertRaises(ValidationError,
                          main_models.Document(description=' .').clean_fields)
        self.assertRaises(ValidationError,
                          main_models.Document(description='<div> .</div>').clean_fields)
        self.assertRaises(ValidationError,
                          main_models.Document(description='&emdash;').clean_fields)

    def test_document_affiliation(self):
        self.assertEqual(self.document.get_affiliation(), self.project)

    def test_has_transcript(self):
        self.assertFalse(self.document.has_transcript())

        transcript = main_models.Transcript.objects.create(
            document_id=self.document.id, creator_id=self.user.id,
            last_updater_id=self.user.id, content='<div>nothing</div>')
        updated_document = main_models.Document.objects.get(id=self.document.id)
        self.assertTrue(updated_document.has_transcript())
        self.assertEqual(updated_document.transcript, transcript)


class NoteTransactionTestCase(FastFixtureTestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.project = Project.objects.get(slug='emma')
        self.user = self.project.members.all()[0]

    def testAssignTopicTwice(self):
        note = main_models.Note.objects.create(
            title='test note',
            markup=u'# hey\n\nthis is a _note_', 
            creator=self.user, last_updater=self.user, project=self.project)
        topic = main_models.Topic.objects.get_or_create_by_name(
            u'Example', self.project, self.user)
        note.related_topics.create(topic=topic, creator=self.user)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
              note.related_topics.create(topic=topic, creator=self.user)

        note.delete()
        topic.delete()

class NewUserTestCase(TestCase):
    def setUp(self):
        self.user = create_test_user()
    def test_create_new_user(self):
        new_user_email = 'fakeperson@example.com'

        test_project = Project.objects.create(
            name='Editors\' Notes\' Idiot Brigade',
            slug='ENIB',
        )
        test_role = test_project.roles.get_or_create_by_name('editor')

        # We haven't invited this person yet, so this shouldn't make an account
        self.assertEqual(create_invited_user(new_user_email), None)
        
        ProjectInvitation.objects.create(
            project=test_project,
            email=new_user_email,
            project_role=test_role,
            creator=self.user
        )
        new_user = create_invited_user(new_user_email)

        self.assertTrue(isinstance(new_user, User))
        self.assertEqual(ProjectInvitation.objects.count(), 0)
        self.assertEqual(new_user.username, 'fakeperson')

class ProjectTopicTestCase(TestCase):
    fixtures = ['projects.json']
    def setUp(self):
        self.project = Project.objects.get(slug='emma')
        self.user = self.project.members.all()[0]
        self.project2 = Project.objects.get(slug='sanger')
        self.user2 = self.project2.members.all()[0]

    def test_create_project_topic(self):
        topic_node, topic = main_models.Topic.objects.create_along_with_node(
            u'Emma Goldman', self.project, self.user)

        self.assertTrue(isinstance(topic_node, main_models.TopicNode))

        topic2 = main_models.Topic.objects.create_from_node(
            topic_node, self.project2, self.user2, name=u'Emma Goldman!!!')

        self.assertEqual(topic_node, topic2.topic_node)
        self.assertEqual(topic_node.get_connected_projects().count(), 2)

    def test_merge_topic_nodes(self):
        _, good_topic = main_models.Topic.objects.create_along_with_node(
            'Emma Goldman', self.project, self.user)
        _, bad_topic = main_models.Topic.objects.create_along_with_node(
            u'Емма Голдман', self.project, self.user)

        bad_topic.merge_into(good_topic)

        bad_node = bad_topic.topic_node
        good_node = good_topic.topic_node

        self.assertEqual(bad_topic.deleted, True)
        self.assertEqual(bad_node.deleted, True)
        self.assertEqual(bad_topic.merged_into, good_topic)
        self.assertEqual(bad_node.merged_into, good_node)
        self.assertEqual(good_node.get_connected_projects().count(), 1)

class ProjectSpecificPermissionsTestCase(TestCase):
    fixtures = ['projects.json']
    def setUp(self):
        self.project = Project.objects.create(
            name='Alexander Berkman Papers Project',
            slug='abpp')
        self.user = User.objects.create(
            username='jd',
            first_name='John',
            last_name='Doe',
            is_superuser=False)
        role = self.project.roles.get_or_create_by_name(
            'Editor', is_super_role=True)
        role.users.add(self.user)

    def test_super_role(self):
        from management import get_all_project_permissions

        role = self.project.roles.get()
        self.assertEqual(role, self.project.roles.get_for_user(self.user))

        # "Super roles" should have all project-specific permissions
        self.assertEqual(len(self.user.get_project_permissions(self.project)),
                         len(get_all_project_permissions()))

        self.assertTrue(self.user.has_project_perm(self.project, 'main.add_note'))

        # Even if this is a super-role, return False for a made up permission.
        # Maybe not, though?
        self.assertFalse(self.user.has_project_perm(self.project, 'made up permission'))

    def test_other_project_perms(self):
        egp = Project.objects.get(slug='emma')

        # User is not a member of this project, so shouldn't have any permissions
        self.assertEqual(egp.roles.get_for_user(self.user), None)
        self.assertEqual(len(self.user.get_project_permissions(egp)), 0)
        self.assertFalse(self.user.has_project_perm(egp, 'main.add_note'))

    def test_limited_role(self):
        # Make a role with only one permission & make sure users of that role
        # can only do that.
        researcher = User.objects.create(username='a_researcher')
        new_role = self.project.roles.get_or_create_by_name('Researcher')
        note_perm = Permission.objects.get_by_natural_key('change_note', 'main', 'note')

        new_role.users.add(researcher)
        new_role.add_permissions(note_perm)

        self.assertEqual(len(researcher.get_project_permissions(self.project)), 1)
        self.assertTrue(researcher.has_project_perm(self.project, 'main.change_note'))
        self.assertFalse(researcher.has_project_perm(self.project, 'main.delete_note'))
        self.assertFalse(researcher.has_project_perm(self.project, 'main.change_topicsummary'))

    def test_invalid_project_permission(self):
        new_role = self.project.roles.get_or_create_by_name('Researcher')
        ok_perm1 = Permission.objects.get_by_natural_key('change_note', 'main', 'note')
        ok_perm2 = Permission.objects.get_by_natural_key('delete_note', 'main', 'note')

        # This isn't a project specific permission
        bad_perm = Permission.objects.get_by_natural_key('add_group', 'auth', 'group')

        new_role.add_permissions(ok_perm1, ok_perm2)
        self.assertRaises(ValueError, new_role.add_permissions, bad_perm)
        self.assertEqual(len(new_role.get_permissions()), 2)

#class OrderedModel(models.Model):
#    name = models.CharField(max_length=10)
#    the_ordering = models.PositiveIntegerField(blank=True, null=True)
#    objects = main_models.base.OrderingManager()
#    class Meta:
#        ordering = ['the_ordering', 'name']
#
#class OrderingTestCase(TestCase):
#    def test_normalize_position_dict(self):
#        position_dict = {
#            'a': 10,
#            'b': 22.5,
#            'c': 5000000
#        }
#        position_dict = main_models.base.OrderingManager\
#                .normalize_position_dict(position_dict, 1)
#        self.assertEqual(sorted(position_dict.items()),
#                         [('a', 1), ('b', 2), ('c', 3)])
#
#        position_dict = main_models.base.OrderingManager\
#                .normalize_position_dict(position_dict, 100)
#        self.assertEqual(sorted(position_dict.items()),
#                         [('a', 100), ('b', 200), ('c', 300)])
#    def test_reordering(self):
#        m3 = OrderedModel.objects.create(name='third')
#        m2 = OrderedModel.objects.create(name='second')
#        m1 = OrderedModel.objects.create(name='first')
#
#        positions = { m1.id: 100, m2.id: 200 }
#        self.assertRaises(ValueError,
#                          OrderedModel.objects.bulk_update_order,
#                          'the_ordering', positions)
#
#        positions[m3.id] = 200.5
#        OrderedModel.objects.bulk_update_order('the_ordering', positions)
#
#        self.assertEqual(tuple(OrderedModel.objects.values_list('id', 'the_ordering')),
#                         ((m1.id, 1), (m2.id, 2), (m3.id, 3)))
#    def test_fill_in_empties(self):
#        m1 = OrderedModel.objects.create(name='a')
#        m2 = OrderedModel.objects.create(name='b')
#        m3 = OrderedModel.objects.create(name='c')
#        m4 = OrderedModel.objects.create(name='d')
#
#        positions = { m1.id: 666, m2.id: 777 }
#        OrderedModel.objects.bulk_update_order('the_ordering', positions,
#                                               fill_in_empty=True, step=10)
#        self.assertEqual(tuple(OrderedModel.objects.values_list('id', 'the_ordering')),
#                         ((m1.id, 10), (m2.id, 20), (m3.id, 30), (m4.id, 40)))
