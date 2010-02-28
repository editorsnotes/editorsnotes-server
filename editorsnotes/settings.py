# Django settings for editorsnotes project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Ryan Shaw', 'ryanshaw@ischool.berkeley.edu'),
)

MANAGERS = ADMINS

TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

# Absolute path to the directory that holds media.
MEDIA_ROOT = ''
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/django_admin_media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'editorsnotes.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'editorsnotes.main',
)

from settings_local import *
