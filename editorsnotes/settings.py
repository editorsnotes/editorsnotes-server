# Django settings for editorsnotes project.

ADMINS = (
    ('Ryan Shaw', 'ryanshaw@ischool.berkeley.edu'),
)

MANAGERS = ADMINS

TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'
DATETIME_FORMAT = 'N j, Y, P'

SITE_ID = 1

USE_L10N = False
USE_I18N = False

# Absolute path to the directory that holds media.
MEDIA_ROOT = ''
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/django_admin_media/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'editorsnotes.urls'

import os.path

TEMPLATE_DIRS = (
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
)

#DEVSERVER_MODULES = (
#    'devserver.modules.sql.SQLRealTimeModule',
#    'devserver.modules.sql.SQLSummaryModule',
#    'devserver.modules.profile.ProfileSummaryModule',
#)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
#    'devserver',
    'editorsnotes.main',
)

from settings_local import *
