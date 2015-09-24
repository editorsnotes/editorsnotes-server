from django.apps import apps as django_apps
from django.apps import AppConfig
from requests.exceptions import ConnectionError

from . import get_index

def register_models(en_index):
    main = django_apps.get_app_config('main')
    en_index.register(main.get_model('Note'),
                      display_field='serialized.title',
                      highlight_fields=('serialized.title',
                                        'serialized.markup_html'))
    en_index.register(main.get_model('Topic'),
                      display_field='serialized.preferred_name',
                      highlight_fields=('serialized.preferred_name',
                                        'serialized.summary'))

    from .types import DocumentTypeAdapter
    class DocumentAdapter(DocumentTypeAdapter):
        display_field = 'serialized.description'
        highlight_fields = ('serialized.description',)
        def get_mapping(self):
            mapping = super(DocumentAdapter, self).get_mapping()
            mapping[self.type_label]['properties']['serialized']['properties'].update({
                'zotero_data': {
                    'properties': {
                        'itemType': {'type': 'string', 'index': 'not_analyzed'},
                        'publicationTitle': {'type': 'string', 'index': 'not_analyzed'},
                        'archive': {'type': 'string', 'index': 'not_analyzed'},
                    }
                }
            })
            return mapping

    en_index.register(main.get_model('Document'), adapter=DocumentAdapter)
    return en_index


default_app_config = 'editorsnotes.search.apps.SearchAppConfig'

class SearchAppConfig(AppConfig):
    name = 'editorsnotes.search'
    verbose_name = "Editors' Notes search"
    def ready(self):
        try:
            en_index = get_index('main')
        except ConnectionError as err:
            raise EnvironmentError(
                'Could not connect to Elasticsearch server at {}. '
                'Is Elasticsearch running?'.format(
                    err.request.url
                ))

        register_models(en_index)
        from . import signals
