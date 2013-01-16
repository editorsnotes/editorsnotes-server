from fabric.api import env, local, lcd
from fabric.decorators import task, runs_once
from fabric.utils import abort

import fileinput
import importlib
import os
import random

import deploy

PROJ_ROOT = os.path.dirname(env.real_fabfile)
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
    with lcd(PROJ_ROOT):
        local('./bin/python manage.py test' % env)

@task
def sync_database():
    "Sync db & run South migrations"
    with lcd(PROJ_ROOT):
        local('./bin/python manage.py syncdb')
        local('./bin/python manage.py migrate')

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
    missing = []
    requirements = (req.rstrip().replace('# symlink: ', '')
                    for req in open('requirements.txt', 'r')
                    if req.startswith('# symlink: '))
    for req in requirements:
        try:
            module = importlib.import_module(req)
        except ImportError:
            missing.append(req)
            continue
        with lcd(os.path.join(PROJ_ROOT, 'lib', 'python2.7', 'site-packages')):
            local('ln -f -s {}'.format(os.path.dirname(module.__file__)))
    if missing:
        abort('Missing python packages: {}'.format(', '.join(missing)))

def collect_static():
    with lcd(PROJ_ROOT):
        local('./bin/python manage.py collectstatic --noinput -v0')

def generate_secret_key():
    SECRET_CHARS = 'abcdefghijklmnopqrstuvwxyz1234567890-=!@#$$%^&&*()_+'
    return ''.join([random.choice(SECRET_CHARS) for i in range(50)])
