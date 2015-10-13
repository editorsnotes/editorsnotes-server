from django.conf import settings
from elasticsearch_dsl import Date, String, Nested, DocType, Object


def base_serialized_field():
    mapping = Object()

    mapping.field('last_updated', Date())
    mapping.field('last_updater', String(index='not_analyzed'))

    mapping.field('created', Date())
    mapping.field('creator', String(index='not_analyzed'))

    project = Object()
    project.field('name', String(index='not_analyzed'))
    project.field('url', String(index='not_analyzed'))
    mapping.field('project', project)

    related_topics = Nested()
    related_topics.field('preferred_name', String(index='not_analyzed'))
    related_topics.field('url', String(index='not_analyzed'))
    mapping.field('related_topics', related_topics)

    mapping.field('references', String(index='not_analyzed', multi=True))
    mapping.field('referenced_by', String(index='not_analyzed', multi=True))

    return mapping


class BaseDocType(DocType):
    serialized = base_serialized_field()
    display_url = String(index='not_analyzed')
    display_title = String(search_analyzer='analyzer_shingle',
                           index_analyzer='analyzer_shingle')


class NoteDocType(BaseDocType):
    class Meta:
        index = settings.ELASTICSEARCH_PREFIX + '-items'
        doc_type = 'note'


class TopicDocType(BaseDocType):
    class Meta:
        index = settings.ELASTICSEARCH_PREFIX + '-items'
        doc_type = 'topic'


class DocumentDocType(BaseDocType):
    serialized = base_serialized_field()\
        .field('zotero_data', Object()
               .field('itemType', String(index='not_analyzed'))
               .field('publicationTitle', String(index='not_analyzed'))
               .field('archive', String(index='not_analyzed')))

    class Meta:
        index = settings.ELASTICSEARCH_PREFIX + '-items'
        doc_type = 'document'
