from django.apps import AppConfig
from requests.exceptions import ConnectionError

from . import items_index, activity_index


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

        from . import signals
