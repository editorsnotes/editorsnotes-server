import os
import subprocess
import time
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

default_browserify = os.path.join(settings.EN_PROJECT_PATH,
                                  'node_modules', '.bin', 'browserify')
browserify_bin = getattr(settings, 'BROWSERIFY_BIN', default_browserify)
                         
watchify_bin = os.path.join(settings.EN_PROJECT_PATH,
                            'node_modules', '.bin', 'watchify')

thisdir = os.path.dirname(__file__)
jsdir = os.path.join('./', 'editorsnotes_app', 'src')


def get_browserify_args(extra_args=None):
    extra_args = set(extra_args) if extra_args else set()

    if settings.DEBUG:
        extra_args.add('-d')

    opts = {
        'base_index': os.path.join(jsdir, 'index-base.js'),
        'admin_index': os.path.join(jsdir, 'index-admin.js'),
        'extra_args': ' '.join(extra_args),
        'base_bundle': os.path.join(settings.STATIC_ROOT, 'base-bundle.js'),
        'admin_bundle': os.path.join(settings.STATIC_ROOT, 'admin-bundle.js'),
        'common_bundle': os.path.join(settings.STATIC_ROOT, 'common-bundle.js')
    }

    command = ('{base_index} {admin_index} {extra_args} '
               '-p [ factor-bundle -o {base_bundle} -o {admin_bundle} ] '
               '-o {common_bundle}')

    return command.format(**opts)


class Command(BaseCommand):
    help = 'Create browserify bundles.'
    option_list = BaseCommand.option_list + (
        make_option('-f',
                    '--fast',
                    action='store_true',
                    help='Speed up browserify compilation time.'),
        make_option('--watch', action='store_true', help='Use watchify.')
    )
    def handle(self, **options):

        if browserify_bin == default_browserify and not os.path.exists(browserify_bin):
            raise CommandError('Browserify not installed. Run `npm install` '
                               'from the base directory.')

        opts = []
        if options.get('fast'):
            opts.append('--fast')

        if options.get('watch', False):
            opts.append('-v')
            args = get_browserify_args(opts)
            self.stdout.write('Running command:\n{} {}'.format(watchify_bin, args))
            proc = subprocess.Popen([watchify_bin] + args.split())
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                proc.kill()

        else:
            args = get_browserify_args(opts)
            self.stdout.write('Running command:\n{} {}'.format(browserify_bin, args))
            subprocess.call([browserify_bin] + args.split())
