from unittest import TestCase

from django.db import models

from rest_framework import serializers

from editorsnotes.auth.models import Project

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


class HydraClassSerializerTestCase(TestCase):
    def setUp(self):
        self.project = Project(slug='egp')

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
