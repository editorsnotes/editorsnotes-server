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

    def test_connect_to_topic_node(self):
        "A user should create a new topic connecting to an existing topic node."
        node_name = u'Емма Голдман'
        topic_node = main_models.TopicNode.objects.create(
            _preferred_name=node_name, creator_id=2, last_updater_id=2)

        add_url = reverse('admin:main_topic_add', kwargs={'project_slug': 'emma'})
        add_url += '?topic_node={}'.format(topic_node.id)

        resp = self.app.get(add_url, user='barry')
        form = resp.forms[1]
        self.assertEqual(form['preferred_name'].value, node_name)

        form['preferred_name'] = 'Emma Goldman'
        resp = form.submit().follow()
        self.assertEqual(resp.context['topic'].topic_node_id, topic_node.id)

        # doing this again should fail, since the project is already connected
        # to the node
        form = self.app.get(add_url, user='barry').forms[1]
        form['preferred_name'] = u'shouldn\'t matter'
        resp = form.submit()
        self.assertEqual(resp.status_code, 200)
        error_messages = resp.forms[1].html.select('.error-message li')
        self.assertEqual(1, len(error_messages))
        self.assertEqual(error_messages[0].text.strip(),
                         u'This project is already connected with topic node '
                         '{}.'.format(topic_node))
