from django.core.urlresolvers import resolve

from ..models import Note, Topic, Document


def models_by_id(Model, ids):
    return Model.objects.filter(id__in=ids)


def rel_els_from_tree(item_type, tree):
    return tree.xpath('//*[@rel="{rel_base}{item_type}"]'.format(
        rel_base='http://editorsnotes.org/v#',
        item_type=item_type
    ))


def kwargs_from_rel_els(rel_els):
    urls = {el.attrib['href'] for el in rel_els}
    return [resolve(url).kwargs for url in urls]


def ensure_same_project(match_kwargs):
    # All should be from the same project
    assert(len({kwargs['project_slug'] for kwargs in match_kwargs}) == 1)


def get_related_notes(tree):
    note_rel_els = rel_els_from_tree('note', tree)
    note_kwargs = kwargs_from_rel_els(note_rel_els)

    if note_kwargs:
        ensure_same_project(note_kwargs)

    return models_by_id(Note, [match['pk'] for match in note_kwargs])


def get_related_topics(tree):
    topic_rel_els = rel_els_from_tree('topic', tree)
    topic_kwargs = kwargs_from_rel_els(topic_rel_els)

    if topic_kwargs:
        ensure_same_project(topic_kwargs)

    return models_by_id(Topic, [match['pk'] for match in topic_kwargs])


def get_related_documents(tree):
    document_rel_els = rel_els_from_tree('document', tree)
    document_kwargs = kwargs_from_rel_els(document_rel_els)

    if document_kwargs:
        ensure_same_project(document_kwargs)

    return models_by_id(Document, [match['pk'] for match in document_kwargs])
