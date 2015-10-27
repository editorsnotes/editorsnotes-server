from django_nose import NoseTestSuiteRunner

from editorsnotes.search import activity_index, items_index

from pyelasticsearch.exceptions import ElasticHttpNotFoundError


ES_INDICES = (items_index, activity_index,)


class CustomTestSuiteRunner(NoseTestSuiteRunner):
    def setup_test_environment(self, **kwargs):
        super(CustomTestSuiteRunner, self).setup_test_environment(**kwargs)

        for index in ES_INDICES:
            try:
                index.delete()
            except ElasticHttpNotFoundError:
                pass

            index.initialize()

    def teardown_test_environment(self, **kwargs):
        super(CustomTestSuiteRunner, self).teardown_test_environment(**kwargs)

        for index in ES_INDICES:
            index.delete()

class NoDBTestSuiteRunner(NoseTestSuiteRunner):
    "Test runner without database creation."
    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass
