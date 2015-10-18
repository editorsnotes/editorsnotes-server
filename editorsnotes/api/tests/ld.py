from django.core.urlresolvers import reverse

from editorsnotes.auth.models import Project, User

from .views import ClearContentTypesTransactionTestCase


class HydraLinksTestCase(ClearContentTypesTransactionTestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.user = User.objects.get(username='barry')
        self.project = Project.objects.get(slug='emma')

    def test_unauthenticated_list_request_operations(self):
        """
        An unauthenticated request should return no supported operations.
        """

        response = self.client.get(
            reverse('api:notes-list', args=[self.project.slug]),
            HTTP_ACCEPT='application/json')

        self.assertEqual(response.data.get('operation'), None)

    def test_authenticated_list_request_operations(self):
        self.client.login(username='barry', password='barry')
        response = self.client.get(
            reverse('api:notes-list', args=[self.project.slug]),
            HTTP_ACCEPT='application/json')

        self.assertEqual(response.data.get('operation'), [{
            'type': 'CreateResourceOperation',
            'title': 'Create a new note',
            'method': 'POST',
            'expects': 'https://workingnotes.org/v#Note',
            'returns': 'https://workingnotes.org/v#Note'
        }])
