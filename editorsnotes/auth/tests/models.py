# -*- coding: utf-8 -*-

from django.contrib.auth.models import Permission
from django.test import TestCase

from ..models import Project, User, ProjectInvitation

def create_user():
    user = User(
        display_name='testuser',
        email='testuser@example.com',
        is_superuser=True)
    user.set_password('testuser')
    user.save()
    return user


# class NewUserTestCase(TestCase):
#     def setUp(self):
#         self.user = create_user()
# 
#     def test_create_new_user(self):
#         new_user_email = 'fakeperson@example.com'
# 
#         test_project = Project.objects.create(
#             name='Editors\' Notes\' Idiot Brigade',
#             slug='ENIB',
#         )
#         test_role = test_project.roles.get_or_create_by_name('editor')
# 
#         ProjectInvitation.objects.create(
#             project=test_project,
#             email=new_user_email,
#             project_role=test_role,
#             creator=self.user
#         )
# 
#         self.assertTrue(isinstance(new_user, User))
#         self.assertEqual(ProjectInvitation.objects.count(), 0)
#         self.assertEqual(new_user.username, 'fakeperson')


class ProjectSpecificPermissionsTestCase(TestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.project = Project.objects.create(
            name='Alexander Berkman Papers Project',
            slug='abpp')
        self.user = User.objects.create(
            email='jd@example.com',
            display_name='John Doe',
            is_superuser=False)
        role = self.project.roles.get_or_create_by_name(
            'Editor', is_super_role=True)
        role.users.add(self.user)

    def test_super_role(self):
        from editorsnotes.main.management import get_all_project_permissions

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
        researcher = User.objects.create(
            email='a_researcher@example.com',
            display_name='a_researcher')
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
