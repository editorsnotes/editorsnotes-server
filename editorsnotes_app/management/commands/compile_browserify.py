import os
import subprocess
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

browserify_bin = os.path.join(settings.EN_PROJECT_PATH,
                              'node_modules', '.bin', 'browserify')

thisdir = os.path.dirname(__file__)
jsdir = os.path.normpath(os.path.join(thisdir, '..', '..', 'js'))
base_index = os.path.join(jsdir, 'index-base.js')
admin_index = os.path.join(jsdir, 'index-admin.js')

class Command(BaseCommand):
    help = 'Create browserify bundles.'
    option_list = BaseCommand.option_list + (
        make_option('-f',
                    '--fast',
                    action='store_true',
                    help='Speed up browserify compilation time.'),
    )
    def handle(self, **options):

        if not os.path.exists(browserify_bin):
            raise CommandError('Browserify not installed. Run `npm install` '
                               'from the base directory.')

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

        if options.get('fast', False):
            browserify_args += ['--fast']
        else:
            subprocess.call(
                [browserify_bin] + browserify_args + base_lib_requires +
                ['-o', os.path.join(settings.STATIC_ROOT, 'base-libs.js')])
            subprocess.call(
                [browserify_bin] + browserify_args + admin_lib_requires + base_lib_excludes +
                ['-o', os.path.join(settings.STATIC_ROOT, 'admin-libs.js')])

        subprocess.call(
            [browserify_bin] + browserify_args + base_lib_excludes +
            [base_index, '-o', os.path.join(settings.STATIC_ROOT, 'base-bundle.js')])

        subprocess.call(
            [browserify_bin] + browserify_args + base_lib_excludes + admin_lib_excludes +
            [admin_index, '-o', os.path.join(settings.STATIC_ROOT, 'admin-bundle.js')])
