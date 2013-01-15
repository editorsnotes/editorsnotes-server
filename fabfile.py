from fabric.api import env, local
from fabric.decorators import task, runs_once

import fileinput
import random

import deploy

env.project_name = 'editorsnotes'

@task
def test():
    "Run the test suite locally."
    local("python manage.py test" % env)

@task
@runs_once
def make_settings():
    """
    Generate a local settings file.

    Without any arguments, this file will go in editorsnotes/settings_local.py.
    If the function is passed an argument that defines env.hosts, this file will
    be placed in this directory with the name settings-{host}.py
    """
    to_create = (['settings-{}.py'.format(host) for host in env.hosts]
                 or ['editorsnotes/settings_local.py'])

    for settings_file in to_create:
        secret_key = generate_secret_key()
        local('cp -n editorsnotes/example-settings_local.py {}'.format(settings_file))
        for line in fileinput.input(settings_file, inplace=True):
            print line.replace("SECRET_KEY = ''",
                               "SECRET_KEY = '{}'".format(secret_key)),

def generate_secret_key():
    SECRET_CHARS = 'abcdefghijklmnopqrstuvwxyz1234567890-=!@#$$%^&&*()_+'
    return ''.join([random.choice(SECRET_CHARS) for i in range(50)])
