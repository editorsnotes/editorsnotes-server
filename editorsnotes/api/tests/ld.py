from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from editorsnotes.auth.models import Project, User
from editorsnotes.main.models import Note

from .views import ClearContentTypesTransactionTestCase


def create_operation(item_type, url):
    return {
        '@id': '_:project_{}_create'.format(item_type.lower()),
        '@type': 'hydra:CreateResourceOperation',
        'label': 'Create a ' + item_type.lower() + ' for this project.',
        'description': None,
        'hydra:method': 'POST',
        'hydra:expects': url + item_type.title(),
        'hydra:returns': url + item_type.title(),
        'hydra:possibleStatus': []
    }


class HydraLinksTestCase(ClearContentTypesTransactionTestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.user = User.objects.get(username='barry')
        self.project = Project.objects.get(slug='emma')
        self.note = Note.objects.create(
            title='A test note',
            project=self.project,
            creator=self.user, last_updater=self.user)

        self.dummy_req = RequestFactory().get('/')

    def test_unauthenticated_hydra_class_request(self):
        """
        An unauthenticated request should return no supported operations.
        """

        response = self.client.get(
            reverse('api:notes-detail',
                    args=[self.project.slug, self.note.id]),
            HTTP_ACCEPT='application/json')

        self.assertTrue('hydra_type' in response.data)
        self.assertTrue(response.data['hydra_type'] in
                        response.data['embedded'])

        hydra_class = response.data['embedded'][response.data['hydra_type']]

        self.assertEqual(len([
            operation for operation
            in hydra_class['hydra:supportedOperation']
            if operation.get('@type') == 'hydra:ReplaceResourceOperation'
        ]), 0)

    def test_authenticated_hydra_class_request(self):
        self.client.login(username='barry', password='barry')

        response = self.client.get(
            reverse('api:notes-detail',
                    args=[self.project.slug, self.note.id]),
            HTTP_ACCEPT='application/json')

        hydra_class = response.data['embedded'][response.data['hydra_type']]

        self.assertEqual(len([
            operation for operation
            in hydra_class['hydra:supportedOperation']
            if operation.get('@type') == 'hydra:ReplaceResourceOperation'
        ]), 1)

    def test_authenticated_user_project_home(self):
        """
        The root resource for an authenticated user should show links to add
        items to all projects.
        """
        self.client.login(username='barry', password='barry')
        response = self.client.get(
            reverse('api:projects-detail', args=[self.project.slug]),
            HTTP_ACCEPT='application/json')

        embedded = response.data.get('embedded')

        self.assertEqual(embedded.keys(), map(
            self.dummy_req.build_absolute_uri,
            [
                '/projects/emma/vocab/#Project',
                '/projects/emma/vocab/#Project/notes',
                '/projects/emma/vocab/#Project/topics',
                '/projects/emma/vocab/#Project/documents',
            ]
        ))

        link_class_embeds = [
            hydra_class for hydra_class in embedded.values()
            if hydra_class['@type'] == 'hydra:Link'
        ]

        self.assertEqual(len(link_class_embeds), 3)

        project_url = self.dummy_req.build_absolute_uri(
            self.project.get_absolute_url())
        project_url += 'vocab/#'

        self.assertEqual([
            link_class['hydra:supportedOperation'][0]
            for link_class in link_class_embeds
        ], [
            create_operation(item_type, project_url)
            for item_type in ('Note', 'Topic', 'Document')
        ])

        self.assertEqual(response.data['@context']['notes'], {
            '@id': self.dummy_req.build_absolute_uri(
                '/projects/emma/vocab/#Project/notes'),
            '@type': '@id'
        })

    def test_authenticated_user_home(self):
        self.client.login(username='barry', password='barry')
        response = self.client.get('/', HTTP_ACCEPT='application/json')

        project_url = self.dummy_req.build_absolute_uri(
            self.project.get_absolute_url())

        self.assertEqual(response.data.get('affiliated_projects').keys(),
                         [project_url])
        self.assertEqual(
            len(response.data['affiliated_projects'].values()[0]['@context']),
            3)
        self.assertEqual(len(response.data.get('embedded')), 3)
