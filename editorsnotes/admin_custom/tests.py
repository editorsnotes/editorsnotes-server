# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from editorsnotes.main.tests import create_test_user
from editorsnotes.main import models as main_models

class TopicAdminTestCase(WebTest):
    fixtures = ['projects.json']
    def create_test_topic(self):
        project = main_models.Project.objects.get(slug='emma');
        node, topic = main_models.Topic.objects.create_along_with_node(
            u'Emma Goldman', project, project.members.get())
        return topic
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

    def test_add_citation(self):
        topic = self.create_test_topic()
        document = main_models.Document.objects.create(
            description="a test document",
            project_id=topic.project_id,
            creator_id=topic.creator_id,
            last_updater_id=topic.last_updater_id)
        url = reverse('admin:main_topic_change',
                      kwargs={'project_slug': 'emma', 'topic_node_id': topic.topic_node_id})

        form = self.app.get(url, user='barry').forms[1]
        form['citation-0-document'] = document.id
        form['citation-0-notes'] = 'it was an interesting thing I found in here'

        resp = form.submit().follow()
        topic = main_models.Topic.objects.get(id=topic.id)
        self.assertEqual(topic.summary_cites.count(), 1)
        self.assertEqual(topic.summary_cites.get().document_id, document.id)
        self.assertEqual(topic.summary_cites.get().object_id, topic.id)

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
