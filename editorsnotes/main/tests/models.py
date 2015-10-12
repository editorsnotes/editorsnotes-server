# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.test import TestCase

from django_nose import FastFixtureTestCase

from editorsnotes.auth.models import Project, User

from .. import models as main_models


class NoteTestCase(TestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.project = Project.objects.get(slug='emma')
        self.user = self.project.members.all()[0]

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
        self.document = main_models.Document.objects\
            .create(**self.document_kwargs)

    def test_hash_description(self):
        self.assertEqual(
            self.document.description_digest,
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
        self.assertRaises(
            ValidationError,
            main_models.Document(description='').clean_fields)
        self.assertRaises(
            ValidationError,
            main_models.Document(description=' ').clean_fields)
        self.assertRaises(
            ValidationError,
            main_models.Document(description=' .').clean_fields)
        self.assertRaises(
            ValidationError,
            main_models.Document(description='<div> .</div>').clean_fields)
        self.assertRaises(
            ValidationError,
            main_models.Document(description='&emdash;').clean_fields)

    def test_document_affiliation(self):
        self.assertEqual(self.document.get_affiliation(), self.project)

    def test_has_transcript(self):
        self.assertFalse(self.document.has_transcript())

        transcript = main_models.Transcript.objects.create(
            document_id=self.document.id, creator_id=self.user.id,
            last_updater_id=self.user.id, content='<div>nothing</div>')
        updated_document = main_models.Document.objects\
            .get(id=self.document.id)
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
