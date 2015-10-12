# -*- coding: utf-8 -*-

from django.contrib.auth.models import Permission
from django.test import TestCase

from ..models import Project, User, ProjectInvitation

from editorsnotes.main.models import Topic, TopicNode
from editorsnotes.main.views.auth import create_invited_user


def create_test_user():
    user = User(username='testuser', is_staff=True, is_superuser=True)
    user.set_password('testuser')
    user.save()
    return user


class NewUserTestCase(TestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_create_new_user(self):
        new_user_email = 'fakeperson@example.com'

        test_project = Project.objects.create(
            name='Editors\' Notes\' Idiot Brigade',
            slug='ENIB',
        )
        test_role = test_project.roles.get_or_create_by_name('editor')

        # We haven't invited this person yet, so this shouldn't make an account
        self.assertEqual(create_invited_user(new_user_email), None)

        ProjectInvitation.objects.create(
            project=test_project,
            email=new_user_email,
            project_role=test_role,
            creator=self.user
        )
        new_user = create_invited_user(new_user_email)

        self.assertTrue(isinstance(new_user, User))
        self.assertEqual(ProjectInvitation.objects.count(), 0)
        self.assertEqual(new_user.username, 'fakeperson')


class ProjectTopicTestCase(TestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.project = Project.objects.get(slug='emma')
        self.user = self.project.members.all()[0]
        self.project2 = Project.objects.get(slug='sanger')
        self.user2 = self.project2.members.all()[0]

    def test_create_project_topic(self):
        topic_node, topic = Topic.objects.create_along_with_node(
            u'Emma Goldman', self.project, self.user)

        self.assertTrue(isinstance(topic_node, TopicNode))

        topic2 = Topic.objects.create_from_node(
            topic_node, self.project2, self.user2, name=u'Emma Goldman!!!')

        self.assertEqual(topic_node, topic2.topic_node)
        self.assertEqual(topic_node.get_connected_projects().count(), 2)

    def test_merge_topic_nodes(self):
        _, good_topic = Topic.objects.create_along_with_node(
            'Emma Goldman', self.project, self.user)
        _, bad_topic = Topic.objects.create_along_with_node(
            u'Емма Голдман', self.project, self.user)

        bad_topic.merge_into(good_topic)

        bad_node = bad_topic.topic_node
        good_node = good_topic.topic_node

        self.assertEqual(bad_topic.deleted, True)
        self.assertEqual(bad_node.deleted, True)
        self.assertEqual(bad_topic.merged_into, good_topic)
        self.assertEqual(bad_node.merged_into, good_node)
        self.assertEqual(good_node.get_connected_projects().count(), 1)


class ProjectSpecificPermissionsTestCase(TestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.project = Project.objects.create(
            name='Alexander Berkman Papers Project',
            slug='abpp')
        self.user = User.objects.create(
            username='jd',
            first_name='John',
            last_name='Doe',
            is_superuser=False)
        role = self.project.roles.get_or_create_by_name(
            'Editor', is_super_role=True)
        role.users.add(self.user)

    def test_super_role(self):
        from management import get_all_project_permissions

        role = self.project.roles.get()
        self.assertEqual(role, self.project.roles.get_for_user(self.user))

        # "Super roles" should have all project-specific permissions
        self.assertEqual(len(self.user.get_project_permissions(self.project)),
                         len(get_all_project_permissions()))

        self.assertTrue(self.user.has_project_perm(
            self.project, 'main.add_note'))

        # Even if this is a super-role, return False for a made up permission.
        # Maybe not, though?
        self.assertFalse(self.user.has_project_perm(
            self.project, 'made up permission'))

    def test_other_project_perms(self):
        egp = Project.objects.get(slug='emma')

        # User is not a member of this project, so shouldn't have any
        # permissions
        self.assertEqual(egp.roles.get_for_user(self.user), None)
        self.assertEqual(len(self.user.get_project_permissions(egp)), 0)
        self.assertFalse(self.user.has_project_perm(egp, 'main.add_note'))

    def test_limited_role(self):
        # Make a role with only one permission & make sure users of that role
        # can only do that.
        researcher = User.objects.create(username='a_researcher')
        new_role = self.project.roles\
            .get_or_create_by_name('Researcher')
        note_perm = Permission.objects\
            .get_by_natural_key('change_note', 'main', 'note')

        new_role.users.add(researcher)
        new_role.add_permissions(note_perm)

        self.assertEqual(len(researcher.get_project_permissions(
            self.project)), 1)
        self.assertTrue(researcher.has_project_perm(
            self.project, 'main.change_note'))
        self.assertFalse(researcher.has_project_perm(
            self.project, 'main.delete_note'))
        self.assertFalse(researcher.has_project_perm(
            self.project, 'main.change_topicmarkup'))

    def test_invalid_project_permission(self):
        new_role = self.project.roles\
            .get_or_create_by_name('Researcher')
        ok_perm1 = Permission.objects\
            .get_by_natural_key('change_note', 'main', 'note')
        ok_perm2 = Permission.objects\
            .get_by_natural_key('delete_note', 'main', 'note')

        # This isn't a project specific permission
        bad_perm = Permission.objects\
            .get_by_natural_key('add_group', 'auth', 'group')

        new_role.add_permissions(ok_perm1, ok_perm2)
        self.assertRaises(ValueError, new_role.add_permissions, bad_perm)
        self.assertEqual(len(new_role.get_permissions()), 2)
