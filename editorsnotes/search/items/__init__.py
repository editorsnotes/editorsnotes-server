from elasticsearch_dsl import analysis

from django.utils.functional import SimpleLazyObject

from ..index import ElasticSearchIndex
from .types import DEFINED_TYPES, DocumentTypeConfig


index = SimpleLazyObject(lambda: ItemsIndex())


class ItemsIndex(ElasticSearchIndex):
    """
    Index for main items: Notes, Topics, and Documents.

    Extends the main index to enable registration of document types which
    associated doc_types to custom mappings and model/serializer classes
    """

    name = 'items'

    def __init__(self):
        super(ItemsIndex, self).__init__()

        # Document type settings by model
        self.document_types = {}

        for model_name, display_field, id_field, highlight_fields in DEFINED_TYPES:
            config = DocumentTypeConfig(
                self.es, self.name, model_name,
                display_field, highlight_fields)
            self.document_types[config.model] = config

    def get_mappings(self):
        mappings = {}
        for type_config in self.document_types.values():
            mappings.update(type_config.type_mapping)
        return mappings

    def get_settings(self):
        shingle_filter = analysis.token_filter(
            'filter_shingle',
            'shingle',
            max_shingle_size=5,
            min_shingle_size=2,
            output_unigrams=True)

        shingle_analyzer = analysis.analyzer(
            'analyzer_shingle',
            tokenizer='standard',
            filter=['standard', 'lowercase', shingle_filter])

        return {
            'settings': {
                'index': {
                    'analysis': shingle_analyzer.get_analysis_definition()
                }
            }
        }

    def make_search_for_model(self, model):
        type_label = self.document_types[model].type_label
        return self.make_search().doc_type(type_label)
