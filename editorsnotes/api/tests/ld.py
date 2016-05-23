import json

from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from editorsnotes.auth.models import Project, User
from editorsnotes.main.models import Note, Topic

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
        self.user = User.objects.get(email='barry@example.com')
        self.project = Project.objects.get(slug='emma')
        self.note = Note.objects.create(
            title='A test note',
            project=self.project,
            creator=self.user, last_updater=self.user)

        self.dummy_req = RequestFactory().get('/')

    def test_unauthenticated_hydra_class_request(self):
        """
        An unauthenticated request should only know about a "GET" operation on
        a project item.
        """
        response = self.client.get(
            reverse('api:notes-detail',
                    args=[self.project.slug, self.note.id]),
            HTTP_ACCEPT='application/json')

        self.assertEqual(len(response.data['hydra:operation']), 1)
        self.assertEqual(response.data['hydra:operation'][0]['hydra:method'],
                         'GET')

    def test_authenticated_hydra_class_request(self):
        """
        An authenticated request with sufficient permissions should know about
        "GET", "PUT", and "POST" operations on a project item.
        """
        self.client.login(username='barry@example.com', password='barry')

        response = self.client.get(
            reverse('api:notes-detail',
                    args=[self.project.slug, self.note.id]),
            HTTP_ACCEPT='application/json')

        self.assertEqual(len(response.data['hydra:operation']), 3)
        self.assertEqual(
            [op['hydra:method'] for op in response.data['hydra:operation']],
            ['PUT', 'DELETE', 'GET'])

    def test_authenticated_user_project_home(self):
        """
        The project resource for an authenticated user should show links to
        add items to all projects.
        """
        self.client.login(username='barry@example.com', password='barry')
        response = self.client.get(
            reverse('api:projects-detail', args=[self.project.slug]),
            HTTP_ACCEPT='application/json')

        embedded = response.data.get('embedded')

        self.assertEqual(list(embedded.keys()), list(map(
            self.dummy_req.build_absolute_uri,
            [
                '/projects/emma/vocab#Project/notes',
                '/projects/emma/vocab#Project/topics',
                '/projects/emma/vocab#Project/documents',
            ]
        )))

        # FIXME: Should be able to update projects' info in the API
        # self.assertEqual(len(response.data.get('hydra:operation')), 3)
        self.assertEqual(len(response.data.get('hydra:operation')), 1)

        link_class_embeds = [
            hydra_class for hydra_class in list(embedded.values())
            if hydra_class['@type'] == 'hydra:Link'
        ]

        self.assertEqual(len(link_class_embeds), 3)

        project_url = self.dummy_req.build_absolute_uri(
            self.project.get_absolute_url())
        project_url += 'vocab#'

        self.assertEqual([
            link_class['hydra:supportedOperation'][0]
            for link_class in link_class_embeds
        ], [
            create_operation(item_type, project_url)
            for item_type in ('Note', 'Topic', 'Document')
        ])

        self.assertEqual(response.data['@context']['notes'], {
            '@id': self.dummy_req.build_absolute_uri(
                '/projects/emma/vocab#Project/notes'),
            '@type': '@id'
        })

    def test_authenticated_user_home(self):
        self.client.login(username='barry@example.com', password='barry')
        response = self.client.get('/', HTTP_ACCEPT='application/json')

        project_url = self.dummy_req.build_absolute_uri(
            self.project.get_absolute_url())

        self.assertEqual(list(response.data.get('affiliated_projects').keys()),
                         [project_url])
        self.assertEqual(
            len(list(response.data['affiliated_projects'].values())[0]['@context']),
            3)
        self.assertEqual(len(response.data.get('embedded')), 3)

class HydraLinksTestCase(ClearContentTypesTransactionTestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.user = User.objects.get(email='barry@example.com')
        self.project = Project.objects.get(slug='emma')
        self.dummy_req = RequestFactory().get('/')
        self.client.login(username='barry@example.com', password='barry')

    def test_topic_ld(self):
        topic = Topic.objects.create(
            preferred_name='Hippolyte Havel',
            project=self.project,
            creator=self.user,
            last_updater=self.user)

        absolute_url = self.dummy_req.build_absolute_uri(topic.get_absolute_url())


        response = self.client.put(
            reverse('api:topics-proj-detail', args=[self.project.slug, topic.id]),
            json.dumps({ 'should': 'disappear' }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        topic.refresh_from_db()
        self.assertEqual(topic.ld, {})


        response = self.client.put(
            reverse('api:topics-proj-detail', args=[self.project.slug, topic.id]),
            json.dumps({
                'should': 'disappear',
                '@id': absolute_url,
                'http://example.com/name': 'Hippolyte Havel'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        topic.refresh_from_db()
        self.assertEqual(topic.ld, {
            '@id': absolute_url,
            'http://example.com/name': 'Hippolyte Havel'
        })
