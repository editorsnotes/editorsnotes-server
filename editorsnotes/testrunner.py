from django.conf import settings
from django_nose import NoseTestSuiteRunner

from editorsnotes.search import items
from editorsnotes.search import activity

from pyelasticsearch.exceptions import IndexAlreadyExistsError

# custom test changes elasticsearch index name
class CustomTestSuiteRunner(NoseTestSuiteRunner):
    def setup_test_environment(self, **kwargs):
        super(CustomTestSuiteRunner, self).setup_test_environment(**kwargs)

        test_index_prefix = settings.ELASTICSEARCH_PREFIX + '-test'
        settings.ELASTICSEARCH_PREFIX = test_index_prefix

        en_index = items.index
        activity_index = activity.index

        en_index.name = en_index.get_name()
        activity_index.name = activity_index.get_name()

        for doctype in en_index.document_types.values():
            doctype.index_name = en_index.name

        try:
            en_index.create()
            activity_index.create()
        except IndexAlreadyExistsError:
            en_index.delete()
            en_index.create()
            activity_index.delete()
            activity_index.create()

    def teardown_test_environment(self, **kwargs):
        super(CustomTestSuiteRunner, self).teardown_test_environment(**kwargs)

        items.index.delete()
        activity.index.delete()
