"""
Utilities for interacting with the markup renderer server.
"""

import json

from lxml import etree, html
import requests

from django.conf import settings


def get_transcluded_items(markup, project):
    url = settings.EDITORSNOTES_MARKUP_RENDERER_URL
    params = {'only_transcluded_items': 1}
    payload = {
        'data': markup,
        'url_root': project.get_absolute_url()
    }

    resp = requests.post(url, params=params, json=payload)

    try:
        items = resp.json()
    except ValueError:
        raise ValueError('Markup renderer server error: {}'.format(resp.text))

    return items


def qs_from_ids(Model, project, ids):
    from ..models import Topic

    if not ids:
        return None

    return Model.objects.filter(project=project, id__in=ids)


def format_items(items_dict, project):
    from ..models import Note, Topic, Document

    items = {}

    notes = qs_from_ids(Note, project, items_dict.get('note'))
    if notes:
        items['note'] = [
            {'id': note.id, 'title': note.title}
            for note in notes
        ]

    topics = qs_from_ids(Topic, project, items_dict.get('topic'))
    if topics:
        items['topic'] = [
            {'id': topic.id, 'preferred_name': topic.preferred_name}
            for topic in topics
        ]

    documents = qs_from_ids(Document, project, items_dict.get('document'))
    if documents:
        items['document'] = [
            {
                'id': document.id,
                'zotero_data': (document.zotero_data and
                                json.loads(document.zotero_data)),
                'description': etree.tostring(document.description)
            }
            for document in documents
        ]

    return items


def get_rendered_markup(markup, items, project):
    url = settings.EDITORSNOTES_MARKUP_RENDERER_URL
    payload = {
        'data': markup,
        'url_root': project.get_absolute_url()
    }
    payload.update(items)

    resp = requests.post(url, json=payload)
    rendered = resp.text

    return rendered


def render_markup(markup, project):
    items_dict = get_transcluded_items(markup, project)
    items = format_items(items_dict, project)
    markup_html = get_rendered_markup(markup, items, project)

    markup_html = markup_html.strip().rstrip()

    return html.fragment_fromstring(markup_html, create_parent='div')
