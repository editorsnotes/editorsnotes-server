import json

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from django.test.client import RequestFactory

from editorsnotes.auth.models import Project

from .views import ClearContentTypesTransactionTestCase
from ..serializers.mixins import EmbeddedItemsMixin
from ..serializers import ProjectSerializer


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
        project_serializer = ProjectSerializer(
            instance=project, context=context)

        class SimpleEmbeddingSerializer(EmbeddedItemsMixin,
                                        serializers.Serializer):
            project_url = serializers.SerializerMethodField()

            class Meta:
                fields = ('project_url',)
                embedded_fields = ('project_url',)

            def get_project_url(self, obj):
                return project_url

        test_serializer = SimpleEmbeddingSerializer({},
            include_embeds=True,
            context=context
        )

        data = json.loads(JSONRenderer().render(test_serializer.data))
        project_data = json.loads(JSONRenderer().render(project_serializer.data))

        self.assertEqual(data, {
            'project_url': project_url,
            '_embedded': {project_url: project_data}
        })
