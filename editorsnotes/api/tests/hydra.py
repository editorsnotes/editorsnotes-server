from unittest import TestCase

from django.db import models

from rest_framework import serializers

from editorsnotes.auth.models import Project
from editorsnotes.search.utils import make_dummy_request

from ..serializers import ProjectSerializer
from ..serializers.hydra import HydraPropertySerializer


class ExampleItem(models.Model):
    required_name = models.TextField(
        help_text='Name that is required.'
    )
    not_required_name = models.TextField(
        blank=True
    )
    read_only_name = models.TextField(
        help_text='Name that cannot be edited.',
        blank=True,
        editable=False
    )


class ExampleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleItem


TEST_CONTEXT = {
    'required_name': 'http://schema.org/name',
    'not_required_name': 'http://schema.org/name',
    'read_only_name': 'http://schema.org/name'
}


class HydraPropertySerializerTestCase(TestCase):
    def setUp(self):
        self.project = Project(slug='egp')
        self.maxDiff = None

    def test_required_property(self):
        serializer = ExampleItemSerializer()
        field = serializer.get_fields()['required_name']

        property_serializer = HydraPropertySerializer(
            field, 'required_name', context_dict=TEST_CONTEXT)

        self.assertEqual(property_serializer.data, {
            'property': 'http://schema.org/name',
            'hydra:description': 'Name that is required.',
            'hydra:title': 'required_name',
            'hydra:required': True,
            'hydra:readonly': False,
            'hydra:writeonly': False
        })

    def test_nonrequired_property(self):
        serializer = ExampleItemSerializer()
        field = serializer.get_fields()['not_required_name']

        property_serializer = HydraPropertySerializer(
            field, 'not_required_name', context_dict=TEST_CONTEXT)

        self.assertEqual(property_serializer.data, {
            'property': 'http://schema.org/name',
            'hydra:description': None,
            'hydra:title': 'not_required_name',
            'hydra:required': False,
            'hydra:readonly': False,
            'hydra:writeonly': False
        })

    def test_read_only_property(self):
        serializer = ExampleItemSerializer()
        field = serializer.get_fields()['read_only_name']

        property_serializer = HydraPropertySerializer(
            field, 'read_only_name', context_dict=TEST_CONTEXT)

        self.assertEqual(property_serializer.data, {
            'property': 'http://schema.org/name',
            'hydra:description': 'Name that cannot be edited.',
            'hydra:title': 'read_only_name',
            'hydra:required': False,
            'hydra:readonly': True,
            'hydra:writeonly': False
        })

    def test_read_only_hyperlinked_collection_property(self):
        serializer = ProjectSerializer(
            self.project, context={'request': make_dummy_request()})
        field = serializer.get_fields()['notes']

        property_serializer = HydraPropertySerializer(
            field, 'notes',
            'emma:Project',
            self.project
        )

        serialized_property = dict(property_serializer.data.items())
        hydra_property = dict(serialized_property.pop('property').items())

        self.assertDictEqual(hydra_property, {
            '@id': 'emma:Project/notes',
            '@type': 'hydra:Link',
            'label': 'notes',
            'hydra:description': 'Notes for this project.',
            'domain': 'emma:Project',
            'range': 'hydra:Collection',
            'hydra:supportedOperation': [
                {
                    '@id': '_:project_notes_retrieve',
                    '@type': 'hydra:Operation',
                    'hydra:method': 'GET',
                    'label': 'Retrieve all notes for this project.',
                    'description': None,
                    'expects': None,
                    'returns': 'hydra:Collection',
                    'statusCodes': []
                }
            ]
        })

        self.assertDictEqual(serialized_property, {
            'hydra:description': 'Notes for this project.',
            'hydra:title': 'notes',
            'hydra:required': False,
            'hydra:readonly': True,
            'hydra:writeonly': False
        })
