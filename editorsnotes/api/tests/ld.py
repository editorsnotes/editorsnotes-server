from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from editorsnotes.auth.models import Project, User

from .views import ClearContentTypesTransactionTestCase


NOTE_CREATE_OPERATION = {
    'type': 'CreateResourceOperation',
    'title': 'Create a new note',
    'method': 'POST',
    'expects': 'https://workingnotes.org/v#Note',
    'returns': 'https://workingnotes.org/v#Note'
}

DOCUMENT_CREATE_OPERATION = {
    'type': 'CreateResourceOperation',
    'title': 'Create a new document',
    'method': 'POST',
    'expects': 'https://workingnotes.org/v#Document',
    'returns': 'https://workingnotes.org/v#Document'
}

TOPIC_CREATE_OPERATION = {
    'type': 'CreateResourceOperation',
    'title': 'Create a new topic',
    'method': 'POST',
    'expects': 'https://workingnotes.org/v#Topic',
    'returns': 'https://workingnotes.org/v#Topic'
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

        self.assertEqual(response.data.get('operation'), None)

    def test_authenticated_list_request_operations(self):
        self.client.login(username='barry', password='barry')
        response = self.client.get(
            reverse('api:notes-list', args=[self.project.slug]),
            HTTP_ACCEPT='application/json')

        self.assertEqual(response.data.get('operation'),
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
                'url': dummy_req.build_absolute_uri(
                    '/projects/emma/doc/#notes'),
                'type': 'Link',
                'title': 'Note list',
                'supportedOperation': [NOTE_CREATE_OPERATION]
            },
            {
                'url': dummy_req.build_absolute_uri(
                    '/projects/emma/doc/#topics'),
                'type': 'Link',
                'title': 'Topic list',
                'supportedOperation': [TOPIC_CREATE_OPERATION]
            },
            {
                'url': dummy_req.build_absolute_uri(
                    '/projects/emma/doc/#documents'),
                'type': 'Link',
                'title': 'Document list',
                'supportedOperation': [DOCUMENT_CREATE_OPERATION]
            }
        ])

        self.assertEqual(response.data['@context']['notes'], {
            '@id': dummy_req.build_absolute_uri('/projects/emma/doc/#notes'),
            '@type': '@id'
        })

    def test_authenticated_user_home(self):
        self.client.login(username='barry', password='barry')
        response = self.client.get('/me/', HTTP_ACCEPT='application/json')

        dummy_req = RequestFactory().get('/')
        project_url = dummy_req.build_absolute_uri(
            self.project.get_absolute_url())

        self.assertEqual(response.data.get('projects').keys(), [project_url])
        self.assertEqual(len(response.data['projects'].values()[0]['@context']), 3)
        self.assertEqual(len(response.data.get('links')), 3)

# In user homepage:
# 'projects': {
#     'https://workingnotes.org/projects/emma/': {
#         '@context': {
#             'notes': 'emma:notes',
#             'documents': 'emma:documents',
#             'topics': 'emma:topics'
#         },
#         'name': 'Emma Goldman Papers',
#     }
# },
