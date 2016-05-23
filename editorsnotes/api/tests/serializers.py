import json

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from django.test.client import RequestFactory

from editorsnotes.auth.models import Project
from editorsnotes.main import models as main_models

from .views import ClearContentTypesTransactionTestCase

from .. import serializers as en_serializers
from ..serializers.mixins import EmbeddedItemsMixin


class EmbeddingSerializerTestCase(ClearContentTypesTransactionTestCase):
    fixtures = ['projects.json']

    def setUp(self):
        factory = RequestFactory()
        self.dummy_request = factory.get('/')

    def test_has_embedded_project(self):
        context = {'request': self.dummy_request}

        project = Project.objects.get(slug='emma')
        project_url = self.dummy_request.build_absolute_uri(
            project.get_absolute_url())
        project_serializer = en_serializers.ProjectSerializer(
            instance=project, context=context)

        class SimpleEmbeddingSerializer(EmbeddedItemsMixin,
                                        serializers.Serializer):
            project_url = serializers.SerializerMethodField()

            class Meta:
                fields = ('project_url',)
                embedded_fields = ('project_url',)

            def get_project_url(self, obj):
                return project_url

        test_serializer = SimpleEmbeddingSerializer(
            {},
            include_embeds=True,
            context=context
        )

        data = json.loads(JSONRenderer().render(test_serializer.data).decode('utf-8'))
        project_data = json.loads(
            JSONRenderer().render(project_serializer.data).decode('utf-8'))

        self.assertEqual(data, {
            'project_url': project_url,
            'embedded': {project_url: project_data}
        })


class DocumentSerializerTestCase(ClearContentTypesTransactionTestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.dummy_request = RequestFactory().get('/')
        self.context = {'request': self.dummy_request}

        self.project = Project.objects.get(slug='emma')
        self.user = self.project.members.get()

        self.document = main_models.Document.objects.create(
            creator=self.user,
            last_updater=self.user,
            project=self.project,
            description='<div>Title</div>'
        )

    def test_document_serializer(self):
        serializer = en_serializers.DocumentSerializer(
            instance=self.document, context=self.context,
            include_embeds=True)

        transcript_url = self.dummy_request.build_absolute_uri(
            '/projects/emma/documents/{}/transcript/'.format(self.document.id))

        self.assertEqual(serializer.data['transcript'], transcript_url)
        self.assertEqual(serializer.data['embedded'][transcript_url], None)

        transcript = main_models.Transcript.objects.create(
            creator=self.user,
            last_updater=self.user,
            document=self.document,
            markup='What the text says.'
        )

        self.assertEqual(
            self.dummy_request.build_absolute_uri(
                transcript.get_absolute_url()),
            transcript_url)

        serializer = en_serializers.DocumentSerializer(
            instance=self.document, context=self.context,
            include_embeds=True)
        self.assertNotEqual(serializer.data['embedded'][transcript_url], None)


class TopicSerializerTestCase(ClearContentTypesTransactionTestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.dummy_request = RequestFactory().get('/')
        self.context = {'request': self.dummy_request}

        self.project = Project.objects.get(slug='emma')
        self.user = self.project.members.get()

        self.topic = main_models.Topic.objects.create(
            creator=self.user,
            last_updater=self.user,
            project=self.project,
            preferred_name='Emma Goldman'
        )

    def test_topic_serializer(self):
        serializer = en_serializers.TopicSerializer(
            instance=self.topic,
            context=self.context,
            include_embeds=True
        )

        base_url = self.dummy_request.build_absolute_uri(
            self.topic.get_absolute_url())
        wn_topic_url = base_url + 'w/'
        project_topic_url = base_url + 'p/'

        self.assertEqual(serializer.data['url'], base_url)

        self.assertDictEqual(serializer.data['wn_data'], {
            "@graph": {
                "@id": wn_topic_url,
                "@graph": {
                    "url": base_url,
                    "preferred_name": "Emma Goldman",
                    "alternate_names": [],
                    "related_topics": [],
                    "markup": None,
                    "markup_html": None
                }
            }
        })

        self.assertDictEqual(serializer.data['linked_data'], {
            "@graph": {
                "@id": project_topic_url,
                "@graph": {}
            }
        })
