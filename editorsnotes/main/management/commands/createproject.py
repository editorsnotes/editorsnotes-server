from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import reversion

from editorsnotes.main.models import Project, User

class Command(BaseCommand):
    args = '"<project_name>" <project_slug>'
    label = ''
    help = 'Create a project'
    option_list = BaseCommand.option_list + (
        make_option('-u',
                    '--users',
                    action='store',
                    help=('comma-separated list of users to be added to the '
                          'project (optional)')),
    )
    def handle(self, *args, **options):
        try:
            project_name, project_slug = args
        except ValueError:
            raise CommandError('Incorrect number of arguments. Usage is:\n'
                               'createproject "<project_name>" <project_slug> '
                               '[--users]')

        usernames = options['users'].split(',') if options['users'] else []
        users = User.objects.filter(username__in=usernames)
        if not len(users) == len(usernames):
            bad_usernames = (set(usernames) - 
                             set(users.values_list('username', flat=True)))
            raise CommandError('The following are not valid users:\n'
                               '{}'.format(', '.join(bad_usernames)))

        self.create_project(project_name, project_slug, users)

    @transaction.commit_on_success
    def create_project(self, name, slug, users):
        with reversion.create_revision():
            project = Project.objects.create(name=name, slug=slug)
            if users:
                editor_role = project.roles.get()
                editor_role.users.add(*users)
        self.stdout.write('Created new project "{}".'.format(project.name))
