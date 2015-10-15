import json
from collections import OrderedDict
from urllib2 import urlopen, HTTPError

from lxml import etree

from django.core.cache import cache

NS = {
    'xhtml': 'http://www.w3.org/1999/xhtml',
    'zot': "http://zotero.org/ns/api",
    'atom': "http://www.w3.org/2005/Atom"
}

ZOTERO_BASE_URL = 'https://api.zotero.org'


def get_item_types():
    url = ZOTERO_BASE_URL + '/itemTypes'
    if not cache.get('item_types'):
        resp = urlopen(url)
        data = resp.read()
        resp.close()
        cache.set('item_types', data, 60 * 24 * 7)
    data = json.loads(cache.get('item_types'))

    from editorsnotes.main.models import Document
    from editorsnotes.search import items
    en_index = items.index
    facet_search = en_index.search_model(Document, {
        'query': {'filtered': {'query': {'match_all': {}}}},
        'facets': {
            'itemTypes': {
                'terms': {
                    'field': 'serialized.zotero_data.itemType',
                    'size': 10
                }
            }
        }
    })

    used_item_types = facet_search['facets']['itemTypes']['terms']

    return {
        'itemTypes': data,
        'common': [item_type['term'] for item_type in used_item_types[:10]]
    }


def get_item_template(item_type):
    if not cache.get('item_template_%s' % item_type):
        url = '%s/items/new?itemType=%s' % (ZOTERO_BASE_URL, item_type)
        page = urlopen(url)
        new_item = page.read()
        cache.set('item_template_%s' % item_type, new_item, 60 * 24 * 7)
    template = cache.get('item_template_%s' % item_type)
    return json.loads(template, object_pairs_hook=OrderedDict)


def get_creator_name(contributor):
    name = contributor.get('lastName') or contributor.get('name') or ''
    name += ', %s' % (
        contributor.get('firstName')
        if contributor.get('firstName')
        else ''
    )
    return name or None


def parse_xml(url):
    try:
        zotero_url = ZOTERO_BASE_URL + url
        page = urlopen(zotero_url)
        xml_parse = etree.parse(page)
        page.close()
        root = xml_parse.getroot()
        return {
            'items': root.xpath('./atom:entry', namespaces=NS),
            'count': root.xpath('./zot:totalResults', namespaces=NS)[0].text
        }
    except HTTPError, error:
        error_content = error.read()
        raise Exception(error_content)
