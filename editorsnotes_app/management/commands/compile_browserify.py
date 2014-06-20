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
jsdir = os.path.normpath(os.path.join(thisdir, '..', '..', 'js'))
base_index = os.path.join(jsdir, 'index-base.js')
admin_index = os.path.join(jsdir, 'index-admin.js')

external_admin_libs = (
    os.path.join(jsdir, 'lib', 'citeproc-js', 'citeproc.js'),
    'backbone',
    'backbone.cocktail',
    'underscore',
)

external_base_libs = (
    os.path.join(jsdir, 'jquery.js'),
    os.path.join(jsdir, 'utils', 'i18n.js'),
)

def get_browserify_args(fast=False, exclude_libs=False):
    commands = {}

    browserify_args = ['-d']

    base_lib_requires = []
    base_lib_excludes = []
    admin_lib_requires = []
    admin_lib_excludes = []
    for lib in external_base_libs:
        base_lib_requires += ['-r', lib]
        base_lib_excludes += ['-x', lib] 
    for lib in external_admin_libs:
        admin_lib_requires += ['-r', lib]
        admin_lib_excludes += ['-x', lib]

    if not exclude_libs:
        commands['base-libs.js'] = (
            browserify_args +
            base_lib_requires + 
            ['-o', os.path.join(settings.STATIC_ROOT, 'base-libs.js')])
        commands['admin-libs.js'] = (
            browserify_args +
            admin_lib_requires +
            base_lib_excludes +
            ['-o', os.path.join(settings.STATIC_ROOT, 'admin-libs.js')])
    commands['base-bundle.js'] = (
        browserify_args +
        ['--fast'] if fast else [] +
        base_lib_excludes +
        [base_index, '-o', os.path.join(settings.STATIC_ROOT, 'base-bundle.js')])
    commands['admin-bundle.js'] = (
        browserify_args +
        ['--fast'] if fast else [] +
        base_lib_excludes +
        admin_lib_excludes +
        [admin_index, '-o', os.path.join(settings.STATIC_ROOT, 'admin-bundle.js')])

    return commands



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

        if options.get('watch', False):
            watchify_procs = []
            commands = get_browserify_args(exclude_libs=True)
            for args in commands.values():
                proc = subprocess.Popen([watchify_bin] + args + ['-v'])
                watchify_procs.append(proc)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                for proc in watchify_procs:
                    proc.kill()

        else:
            fast = exclude_libs = options.get('fast')
            commands = get_browserify_args(fast, exclude_libs)
            for args in commands.values():
                subprocess.call([browserify_bin] + args)
