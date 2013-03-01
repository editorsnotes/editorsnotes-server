# -*- coding: utf-8 -*-

from django.test import TestCase
from editorsnotes.main.tests import create_test_user
from editorsnotes.main.models import Topic

class TopicAdminTestCase(TestCase):
    def setUp(self):
        self.user = create_test_user()
        self.topics = []
        self.topics.append(Topic.objects.create(
            preferred_name=u'Ленинь, Владимир Ильич',
            summary=u'Мужчина; коммунисть.',
            creator=self.user, last_updater=self.user))
        self.topics.append(Topic.objects.create(
            preferred_name=u'Goldman, Emma',
            summary=u'Nowhere at home.',
            creator=self.user, last_updater=self.user))
        self.topics.append(Topic.objects.create(
            preferred_name=u'Doe, John', 
            summary='A simple man.',
            creator=self.user, last_updater=self.user))
        self.client.login(username='testuser', password='testuser')
    def tearDown(self):
        for t in self.topics:
            t.delete()
    def test_duplicate_slug(self):
        response = self.client.post(
            '/admin/main/topic/add/', 
            {
                'preferred_name': u'Doe, John',
                'summary': u'John Doe was a great man.',
                'alias-TOTAL_FORMS': 0,
                'alias-INITIAL_FORMS': 0,
                'alias-MAX_NUM_FORMS': 0,
                'citation-TOTAL_FORMS': 0,
                'citation-INITIAL_FORMS': 0,
                'citation-MAX_NUM_FORMS': 0,
                'topicassignment-TOTAL_FORMS': 0,
                'topicassignment-INITIAL_FORMS': 0,
                'topicassignment-MAX_NUM_FORMS': 0,
            }
        )
        self.assertFormError(
            response, 'form', 'preferred_name',
            u'Topic with this Preferred name already exists.')
    def test_similar_slug(self):
        self.assertTrue(self.client.login(username='testuser', password='testuser'))
        response = self.client.post(
            '/admin/main/topic/add/', 
            {
                'preferred_name': u'Doe John',
                'summary': u'John Doe was a great man.',
                'alias-TOTAL_FORMS': 0,
                'alias-INITIAL_FORMS': 0,
                'alias-MAX_NUM_FORMS': 0,
                'citation-TOTAL_FORMS': 0,
                'citation-INITIAL_FORMS': 0,
                'citation-MAX_NUM_FORMS': 0,
                'topicassignment-TOTAL_FORMS': 0,
                'topicassignment-INITIAL_FORMS': 0,
                'topicassignment-MAX_NUM_FORMS': 0,
            }
        )
        self.assertFormError(
            response, 'form', 'preferred_name',
            u'Topic with a very similar Preferred name already exists.')
