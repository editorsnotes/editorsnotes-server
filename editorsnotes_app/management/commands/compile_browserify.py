import os
import subprocess
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

browserify_bin = os.path.join(settings.EN_PROJECT_PATH,
                              'node_modules', '.bin', 'browserify')

thisdir = os.path.dirname(__file__)
base_index = os.path.join(thisdir, '..', '..', 'js', 'index-base.js')
admin_index = os.path.join(thisdir, '..', '..', 'js', 'index-base.js')

class Command(BaseCommand):
    help = 'Create browserify bundles.'
    option_list = BaseCommand.option_list + (
        make_option('-f',
                    '--fast',
                    action='store_true',
                    help='Speed up browserify compilation time.'),
    )
    def handle(self, *args, **options):

        if args:
            raise CommandError('This command does not take any args.')

        if not os.path.exists(browserify_bin):
            raise CommandError('Browserify not installed. Run `npm install` '
                               'from the base directory.')

        browserify_args = []

        if options.get('fast', False):
            browserify_args += []

        subprocess.call([browserify_bin] + browserify_args + [
            base_index, '-o',
            os.path.join(settings.STATIC_ROOT, 'base-bundle.js')
        ])

        subprocess.call([browserify_bin] + browserify_args + [
            admin_index, '-o',
            os.path.join(settings.STATIC_ROOT, 'admin-bundle.js')
        ])
