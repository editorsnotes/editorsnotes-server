import sys

from .settings import *

ELASTICSEARCH_PREFIX = '-test-' + ELASTICSEARCH_PREFIX
SITE_URL = 'http://testserver/'

NO_DB_TEST = (
    len(sys.argv) > 1 and
    sys.argv[1] == 'test' and
    '--no-test-db' in sys.argv
)

if NO_DB_TEST:
    sys.argv.pop(sys.argv.index('--no-test-db'))
    TEST_RUNNER = 'editorsnotes.testrunner.NoDBTestSuiteRunner'
