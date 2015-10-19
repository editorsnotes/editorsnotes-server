from fabric.api import env, local, lcd
from fabric.colors import red, green
from fabric.decorators import task, runs_once
from fabric.operations import prompt
from fabric.utils import abort

import datetime
import fileinput
import importlib
import os
import random
import re
import subprocess
import sys
import time

PROJ_ROOT = os.path.dirname(env.real_fabfile)
env.project_name = 'editorsnotes'
env.python = 'python' if 'VIRTUAL_ENV' in os.environ else './bin/python'

@task
def setup():
    """
    Set up a local development environment

    This command must be run with Fabric installed globally (not inside a
    virtual environment)
    """
    if os.getenv('VIRTUAL_ENV') or hasattr(sys, 'real_prefix'):
        abort(red('Deactivate any virtual environments before continuing.'))
    make_settings()
    make_virtual_env()
    collect_static()
    print ('\nDevelopment environment successfully created.\n' +
           'Create a Postgres database, enter its information into ' +
           'editorsnotes/settings_local.py, and run `fab sync_database` to finish.')

@task
def test():
    "Run the test suite locally."
    with lcd(PROJ_ROOT):
        local('{python} manage.py test'.format(**env))

@task
def sync_database():
    "Sync db, make cache tables, and run South migrations"

    new_installation = len(get_db_tables()) == 0

    with lcd(PROJ_ROOT):
        create_cache_tables()
        local('{python} manage.py migrate --noinput'.format(**env))

    if new_installation:
        print('\nDatabase synced. Follow prompts to create an initial '
              'super user and project.')
        username = prompt('Username: ', validate=str)
        local('{python} manage.py createsuperuser --username {username}'.format(
            username=username, **env))

        project_name = prompt('Project name (blank to skip): ')
        if project_name:
            project_slug = prompt('Project slug: ', validate=str)

            local('{python} manage.py createproject '
                  '"{name}" {slug} --users={username}'.format(
                      name=project_name, slug=project_slug,
                      username=username, **env))

@task
def runserver():
    "Run the development server"
    with lcd(PROJ_ROOT):
        local('{python} manage.py runserver'.format(**env))

@task
def generate_blank_settings():
    settings_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'editorsnotes/example-settings_local.py')
    secret_key = generate_secret_key()

    with open(settings_path) as settings_file:
        settings_str = settings_file.read()

    settings_str = settings_str.replace(
        "SECRET_KEY = ''", "SECRET_KEY = '{}'".format(secret_key))

    print settings_str
    return settings_str

@task
@runs_once
def make_settings():
    """
    Generate a local settings file.

    Without any arguments, this file will go in editorsnotes/settings_local.py.
    If the function is passed an argument that defines env.hosts, this file will
    be placed in the deploy directory with the name settings-{host}.py
    """
    to_create = (['deploy/settings-{}.py'.format(host) for host in env.hosts]
                 or ['editorsnotes/settings_local.py'])

    for settings_file in to_create:
        secret_key = generate_secret_key()
        with lcd(PROJ_ROOT):
            local('if [ ! -f {0} ]; then cp {1} {0}; fi'.format(
                settings_file, 'editorsnotes/example-settings_local.py'))
            for line in fileinput.input(settings_file, inplace=True):
                print line.replace("SECRET_KEY = ''",
                                   "SECRET_KEY = '{}'".format(secret_key)),

@task
def create_cache_tables():
    caches = ['zotero_cache']
    tables = get_db_tables()
    for cache in caches:
        if "'{}'".format(cache) in tables:
            continue
        with lcd(PROJ_ROOT):
            local('{python} manage.py createcachetable {cache}'.format(cache=cache, **env))


ADMIN_CSS_IN = './editorsnotes/auth/static/admin.css'
ADMIN_CSS_OUT = './static/admin_compiled.css'
ADMIN_CSS_OUT_DEV = ADMIN_CSS_IN.replace('.css', '_compiled.css')

@task
def compile_admin_css():
    with lcd(PROJ_ROOT):
        local('./node_modules/.bin/cssnext {} {}'.format(
            ADMIN_CSS_IN, ADMIN_CSS_OUT))

@task
def watch_admin_css():
    with lcd(PROJ_ROOT):
        local('./node_modules/.bin/cssnext --watch --verbose {} {}'.format(
            ADMIN_CSS_IN, ADMIN_CSS_OUT_DEV))

def get_db_tables():
    tables = local('{python} manage.py inspectdb | '
                   'grep "db_table =" || true'.format(**env), capture=True)
    return tables or []

def make_virtual_env():
    "Make a virtual environment for local dev use"
    with lcd(PROJ_ROOT):
        local('virtualenv -p python2 .')
        local('./bin/pip install -r requirements.txt')

def collect_static():
    with lcd(PROJ_ROOT):
        local('{python} manage.py collectstatic --noinput -v0'.format(**env))

def generate_secret_key():
    SECRET_CHARS = 'abcdefghijklmnopqrstuvwxyz1234567890-=!@#$$%^&&*()_+'
    return ''.join([random.choice(SECRET_CHARS) for i in range(50)])
