from fabric.api import local
from fabric.contrib import django, files

import fileinput
import random
import sys

django.project('editorsnotes')

def generate_secret_key():
    SECRET_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*_+=-"
    return ''.join([random.choice(SECRET_CHARS) for i in range(50)])

def make_settings():
    local('cp -n editorsnotes/example-settings_local.py editorsnotes/settings_local.py')
    from django.conf import settings
    if not settings.SECRET_KEY:
        files.sed('editorsnotes/settings_local.py',
                  "SECRET_KEY = ''",
                  "SECRET_KEY = '%s'" % generate_secret_key())

def make_virtualenv():
    local('virtualenv .')
    local('./bin/pip install -r requirements.txt')

def collect_static():
    local('./bin/python manage.py collectstatic --noinput -v 0')

def setup():
    make_virtualenv()
    make_settings()
    collect_static()
