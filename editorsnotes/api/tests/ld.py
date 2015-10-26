from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from editorsnotes.auth.models import Project, User

from .views import ClearContentTypesTransactionTestCase


NOTE_CREATE_OPERATION = {
    '@type': 'hydra:CreateResourceOperation',
    'label': 'Create a new note',
    'description': None,
    'hydra:method': 'POST',
    'hydra:expects': 'https://workingnotes.org/v#Note',
    'hydra:returns': 'https://workingnotes.org/v#Note',
    'hydra:statusCode': []
}

DOCUMENT_CREATE_OPERATION = {
    '@type': 'hydra:CreateResourceOperation',
    'label': 'Create a new document',
    'description': None,
    'hydra:method': 'POST',
    'hydra:expects': 'https://workingnotes.org/v#Document',
    'hydra:returns': 'https://workingnotes.org/v#Document',
    'hydra:statusCode': []
}

TOPIC_CREATE_OPERATION = {
    '@type': 'hydra:CreateResourceOperation',
    'label': 'Create a new topic',
    'description': None,
    'hydra:method': 'POST',
    'hydra:expects': 'https://workingnotes.org/v#Topic',
    'hydra:returns': 'https://workingnotes.org/v#Topic',
    'hydra:statusCode': []
}


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

        self.assertEqual(response.data.get('hydra:operation'), None)

    def test_authenticated_list_request_operations(self):
        self.client.login(username='barry', password='barry')
        response = self.client.get(
            reverse('api:notes-list', args=[self.project.slug]),
            HTTP_ACCEPT='application/json')

        self.assertEqual(response.data.get('hydra:operation'),
                         [NOTE_CREATE_OPERATION])

    def test_authenticated_user_project_home(self):
        """
        The root resource for an authenticated user should show links to add
        items to all projects.
        """
        self.client.login(username='barry', password='barry')
        response = self.client.get(
            reverse('api:projects-detail', args=[self.project.slug]),
            HTTP_ACCEPT='application/json')

        dummy_req = RequestFactory().get('/')

        self.assertEqual(response.data.get('links'), [
            {
                '@id': dummy_req.build_absolute_uri(
                    '/projects/emma/doc/#notes'),
                '@type': 'hydra:Link',
                'hydra:title': 'Note list',
                'hydra:supportedOperation': [NOTE_CREATE_OPERATION]
            },
            {
                '@id': dummy_req.build_absolute_uri(
                    '/projects/emma/doc/#topics'),
                '@type': 'hydra:Link',
                'hydra:title': 'Topic list',
                'hydra:supportedOperation': [TOPIC_CREATE_OPERATION]
            },
            {
                '@id': dummy_req.build_absolute_uri(
                    '/projects/emma/doc/#documents'),
                '@type': 'hydra:Link',
                'hydra:title': 'Document list',
                'hydra:supportedOperation': [DOCUMENT_CREATE_OPERATION]
            }
        ])

        self.assertEqual(response.data['@context']['notes'], {
            '@id': dummy_req.build_absolute_uri('/projects/emma/doc/#notes'),
            '@type': '@id'
        })

    def test_authenticated_user_home(self):
        self.client.login(username='barry', password='barry')
        response = self.client.get('/', HTTP_ACCEPT='application/json')

        dummy_req = RequestFactory().get('/')
        project_url = dummy_req.build_absolute_uri(
            self.project.get_absolute_url())

        self.assertEqual(response.data.get('affiliated_projects').keys(), [project_url])
        self.assertEqual(len(response.data['affiliated_projects'].values()[0]['@context']), 3)
        self.assertEqual(len(response.data.get('links')), 3)
