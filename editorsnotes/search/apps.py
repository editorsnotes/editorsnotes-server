import logging

from pyelasticsearch.exceptions import ElasticHttpError
from requests.exceptions import ConnectionError

from django.apps import AppConfig

from . import items_index, activity_index


logger = logging.getLogger(__name__)


class SearchAppConfig(AppConfig):
    name = 'editorsnotes.search'
    verbose_name = "Editors' Notes search"

    def ready(self):
        try:
            items_index.initialize()
            activity_index.initialize()
        except ConnectionError as err:
            raise EnvironmentError(
                'Could not connect to Elasticsearch server at {}. '
                'Is Elasticsearch running?'.format(
                    err.request.url
                ))
        except ElasticHttpError as err:
            is_mapping_err = err.error.startswith('MergeMappingException')

            if not is_mapping_err:
                raise err

            logger.critical(
                u'Encountered error updating mappings in Elasticsearch. '
                'You likely need to run `rebuild_es_index`, or else '
                'Elasticsearch will not run properly.\n\n'
                'Original error was:\n{}\n'.format(err.error))

        from . import signals
