###################
# Locale settings #
###################

# These settings are defaults: change in settings_local.py if desired
TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'
DATETIME_FORMAT = 'N j, Y, P'
USE_L10N = False
USE_I18N = True


########################
# Datebase information #
########################

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2'
        # The rest of the DB configuration is done in settings_local.py
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'zotero_cache'
    }
}
SOUTH_TESTS_MIGRATE = False


#################
# Site settings #
#################

SITE_ID = 1
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
ROOT_URLCONF = 'editorsnotes.urls'

AUTH_USER_MODEL = 'main.User'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/auth/'
LOGIN_URL = '/auth/signin'


#################
# Path settings #
#################
import os

EN_PROJECT_PATH = os.path.abspath(os.path.join(
    os.path.normpath(os.path.dirname(__file__)),
    os.path.pardir
))

#STATICFILES_DIRS = (
#    os.path.join(EN_PROJECT_PATH, 'editorsnotes', 'static'),
#)

# Override these variables in settings_local.py if desired
DEBUG = False
try:
    from settings_local import STORAGE_PATH
except ImportError:
    STORAGE_PATH = EN_PROJECT_PATH

MEDIA_ROOT = os.path.join(STORAGE_PATH, 'uploads')
STATIC_ROOT = os.path.join(STORAGE_PATH, 'static')


###################
# Everything else #
###################

TEST_RUNNER = 'editorsnotes.testrunner.CustomTestSuiteRunner'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'reversion',
    'licensing',
    'rest_framework',
    'rest_framework.authtoken',
    'widget_tweaks',
    'django_nose',
    'editorsnotes.main',
    'editorsnotes.auth',
    'editorsnotes.djotero',
    'editorsnotes.api',
    'editorsnotes.search',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'editorsnotes.api.renderers.JSONLDRenderer',
        'editorsnotes.api.renderers.BrowsableJSONLDRenderer',
        'editorsnotes.api.renderers.TurtleRenderer',
        'editorsnotes.api.renderers.BrowsableTurtleRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25
}

# Add in local settings
from settings_local import *
DATABASES['default'].update(POSTGRES_DB)
try:
    INSTALLED_APPS = INSTALLED_APPS + LOCAL_APPS
except NameError:
    pass

if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'editorsnotes': {
                'handlers': ['console'],
                'level': 'INFO',
            },
        }
    }
