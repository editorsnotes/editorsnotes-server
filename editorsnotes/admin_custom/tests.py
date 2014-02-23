# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from editorsnotes.main.tests import create_test_user
from editorsnotes.main import models as main_models

class TopicAdminTestCase(WebTest):
    fixtures = ['projects.json']
    def test_create_topic(self):
        "A user should be able to create a topic with a unique name."
        topic_name = u'Emma Goldman'
        add_url = reverse('admin:main_topic_add', kwargs={'project_slug': 'emma'})

        form = self.app.get(add_url, user='barry').forms[1]
        form['preferred_name'] = topic_name

        resp = form.submit()
        self.assertEqual(resp.status_code, 302)
        resp = resp.follow()
        self.assertEqual(resp.context['topic'].preferred_name, topic_name)

        # Duplicate should raise an error
        duplicate_form = self.app.get(add_url, user='barry').forms[1]
        form['preferred_name'] = topic_name
        resp = form.submit()
        self.assertEqual(resp.status_code, 200)

        error_messages = resp.forms[1].html.select('.error-message li')
        self.assertEqual(1, len(error_messages))
        self.assertEqual(error_messages[0].text.strip(),
                         u'Topic with this preferred name already exists.')

    def test_create_empty_topic_error(self):
        "A user should not be able to create a topic with an empty name."
        add_url = reverse('admin:main_topic_add', kwargs={'project_slug': 'emma'})

        # Submit a blank form
        resp = self.app.get(add_url, user='barry').forms[1].submit()
        self.assertEqual(resp.status_code, 200)

        error_messages = resp.forms[1].html.select('.error-message li')
        self.assertEqual(1, len(error_messages))
        self.assertEqual(error_messages[0].text.strip(), u'This field is required.')
