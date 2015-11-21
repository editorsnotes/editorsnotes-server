from django.core import mail
from django.test import TestCase

class AuthEmailTestCase(TestCase):
    fixtures = ['projects.json']

    def test_reset_password_email(self):
        req = self.client.post('/auth/account/password_reset', {
            'email': 'fake2@example.com'
        })

        self.assertEqual(req.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

        root = req.wsgi_request\
            .build_absolute_uri('/auth/account/password_reset/')

        self.assertTrue(root in mail.outbox[0].body)
