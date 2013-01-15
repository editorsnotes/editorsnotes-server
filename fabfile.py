from fabric.api import env, local, lcd
from fabric.decorators import task, runs_once
from fabric.utils import abort

import fileinput
import os
import random

import deploy

PROJ_ROOT = os.path.normpath(os.path.join(env.real_fabfile, '..'))
env.project_name = 'editorsnotes'

@task
def setup():
    "Set up a local development environment"
    make_settings()
    make_virtual_env()
    symlink_packages()
    collect_static()

@task
def test():
    "Run the test suite locally."
    local("python manage.py test" % env)

@task
def runserver():
    "Run the development server"
    with lcd(PROJ_ROOT):
        local('./bin/python manage.py runserver')

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
            local('cp -n editorsnotes/example-settings_local.py {}'.format(settings_file))
            for line in fileinput.input(settings_file, inplace=True):
                print line.replace("SECRET_KEY = ''",
                                   "SECRET_KEY = '{}'".format(secret_key)),

def make_virtual_env():
    "Make a virtual environment for local dev use"
    with lcd(PROJ_ROOT):
        local('virtualenv .')
        local('./bin/pip install -r requirements.txt')

def symlink_packages():
    "Symlink python packages not installed with pip"
    try:
        import xapian
    except ImportError:
        abort('Install "xapian" python package in order to continue.')

    try:
        import psycopg2
    except ImportError:
        abort('Install "psycopg2" python package in order to continue.')

    packages = os.path.join(PROJ_ROOT, 'lib', 'python2.7', 'site-packages')
    xapian_path = os.path.normpath(os.path.join(xapian.__file__, '..'))
    psycopg2_path = os.path.normpath(os.path.join(psycopg2.__file__, '..'))

    local('ln -f -s {} {}'.format(xapian_path, packages))
    local('ln -f -s {} {}'.format(psycopg2_path, packages))

def collect_static():
    with lcd(PROJ_ROOT):
        local('./bin/python manage.py collectstatic --noinput -v0')

def generate_secret_key():
    SECRET_CHARS = 'abcdefghijklmnopqrstuvwxyz1234567890-=!@#$$%^&&*()_+'
    return ''.join([random.choice(SECRET_CHARS) for i in range(50)])
