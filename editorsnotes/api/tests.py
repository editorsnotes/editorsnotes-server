# -*- coding: utf-8 -*-

import json
from django.core.urlresolvers import reverse
from django.test import TestCase
from editorsnotes.main.tests import create_test_user
from editorsnotes.main import models

class TopicAPITestCase(TestCase):
    def setUp(self):
        self.user = create_test_user()
        self.client.login(username='testuser', password='testuser')
        self.topics = []
    def tearDown(self):
        for t in self.topics:
            t.delete()
    def test_create_topic(self):
        data = {
            'preferred_name': u'Patrick Golden',
            'summary': u'A writer of tests'
        }

        # Simple topic creation
        response = self.client.post(
            reverse('api-topics-list'),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        # Posting the same data should raise an error
        response = self.client.post(
            reverse('api-topics-list'),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['preferred_name'],
                         [u'Topic with this Preferred name already exists.'])

