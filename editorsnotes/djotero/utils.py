import json
from collections import OrderedDict
from urllib2 import urlopen, HTTPError

from lxml import etree

from django.core.cache import cache
from django.utils.translation import ugettext as _

NS = {'xhtml': 'http://www.w3.org/1999/xhtml',
      'zot' : "http://zotero.org/ns/api",
      'atom' : "http://www.w3.org/2005/Atom"}

ZOTERO_BASE_URL = 'https://api.zotero.org'

def validate_zotero_data(zotero_dict):
    item_type = zotero_dict.has_key('itemType') and len(zotero_dict['itemType'])
    populated_fields = [ v for v in zotero_dict.values()
                               if isinstance(v, basestring) and v ]

    if all([item_type, len(populated_fields) > 1]):
        return True
    else:
        return False

# Zotero API calls
def get_libraries(zotero_uid, zotero_key):
    url = '/users/%s/groups?key=%s' % (zotero_uid, zotero_key)
    access = {'zapi_version' : 'null',
              'libraries' : [{'title' : 'Your library',
                              'location': '/users/%s' % (zotero_uid) }]}
    for x in parse_xml(url)['items']:
        title = x.xpath('./atom:title', namespaces=NS)[0].text
        loc = x.xpath('./atom:link[@rel="self"]', namespaces=NS)[0].attrib['href'].replace(ZOTERO_BASE_URL, '')
        access['libraries'].append({'title' : title, 'location' : loc })
    return access

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

def get_collections(zotero_key, loc, top):
    if top:
        url = '%s/collections/top?key=%s&order=title&format=atom&content=json' % (loc, zotero_key)
    else:
        url = '%s/collections?key=%s&format=atom&content=json' % (loc, zotero_key)
    collections = { 'zapi_version' : 'null',
                    'collections' : []}
    for x in parse_xml(url)['items']:
        title = x.xpath('./atom:title', namespaces=NS)[0].text
        loc = x.xpath('./atom:link[@rel="self"]', namespaces=NS)[0].attrib['href'].replace(ZOTERO_BASE_URL, '')
        has_children = bool(int(x.xpath('./zot:numCollections', namespaces=NS)[0].text))
        collections['collections'].append({ 'title' : title, 'location' : loc, 'has_children' : int(has_children) })
    return collections

def get_items(zotero_key, loc, opts):
    opts = ['%s=%s' % (key, str(opts[key])) for key in opts.keys()]
    url = '%s/items?key=%s&format=atom&content=json&%s' % (loc, zotero_key, '&'.join(opts))
    latest = { 'zapi_version' : 'null', 'items' : []}
    parsed = parse_xml(url)
    latest['total_items'] = parsed['count']
    for x in parsed['items']:
        title = x.xpath('./atom:title', namespaces=NS)[0].text
        library_url = x.xpath('./atom:id', namespaces=NS)[0].text
        item_id = x.xpath('./zot:key', namespaces=NS)[0].text
        item_json = x.xpath('./atom:content[@zot:type="json"]', namespaces=NS)[0].text
        try:
            item_date = json.loads(item_json)['date']
        except:
            item_date = ""
        if json.loads(item_json)['itemType'] not in ['note', 'attachment']:
            latest['items'].append(
                {'title' : title,
                 'item_type' : _(json.loads(item_json)['itemType']),
                 'loc' : loc,
                 'id' : item_id,
                 'date' : item_date,
                 'url' : library_url,
                 'item_json' : item_json })
    return latest

def get_item_template(item_type):
    if not cache.get('item_template_%s' % item_type):
        url = '%s/items/new?itemType=%s' % (ZOTERO_BASE_URL, item_type)
        page = urlopen(url)
        new_item = page.read()
        cache.set('item_template_%s' % item_type, new_item, 60 * 24 * 7)
    template = cache.get('item_template_%s' % item_type)
    return json.loads(template, object_pairs_hook=OrderedDict)

def get_creator_types(item_type):
    if not cache.get('creators_%s' % item_type):
        url = '%s/itemTypeCreatorTypes?itemType=%s' % (ZOTERO_BASE_URL, item_type)
        page = urlopen(url)
        creators = page.read()
        cache.set('creators_%s' % item_type, creators, 60 * 24 * 7)
    creator_types = cache.get('creators_%s' % item_type)
    return json.loads(creator_types, object_pairs_hook=OrderedDict)

def as_readable(zotero_json_string):
    zotero_data_list = []
    zotero_data = json.loads(zotero_json_string, object_pairs_hook=OrderedDict)
    for key, val in zotero_data.items():
        if key == 'itemType':
            readable_data = (key, _(val), 'Item Type')
        elif key == 'creators' and val:
            readable_data = resolve_names(zotero_data, 'readable')
        elif key == 'tags':
            continue
        elif val:
            readable_data = (key, val, _(key))
        else:
            readable_data = False
        if readable_data:
            if isinstance(readable_data, tuple):
                keys = ('zotero_key', 'value', 'label')
                zotero_data_list.append( dict(zip(keys, readable_data)) )
            elif isinstance(readable_data, list):
                zotero_data_list += readable_data
    return zotero_data_list

def get_creator_name(contributor):
    name_parts = [contributor[key] for key in contributor.keys()
                  if key != 'creatorType']
    name = contributor.get('lastName') or contributor.get('name') or ''
    name += ', %s' % contributor.get('firstName') if contributor.get('firstName') else ''
    return name or None

def resolve_names(zotero_data, format):
    if format == 'facets':
        # Data to be used in facets only needs a sortable name, either 'lastName' or 'name'
        contribs = []
        for creator in zotero_data['creators']:
            name = creator.get('lastName') or creator.get('name')
            contribs.append({creator['creatorType'] : name})
        
    if format == 'readable':
        contribs = []
        for creator in zotero_data['creators']:
            # This is needed because blank creators are kept inside the zotero
            # json, for easier inline editing. If a creator doesn't have a name,
            # that data isn't rendered.
            if not any([creator[key] for key in creator.keys()
                        if key != 'creatorType']):
                continue
            name = creator.get('name') or '%(firstName)s %(lastName)s' % creator
            contribs.append({'zotero_key' : creator['creatorType'],
                             'label' : _(creator['creatorType']),
                             'value' : name})
    return contribs

def parse_xml(url):
    try:
        zotero_url = ZOTERO_BASE_URL + url
        page = urlopen(zotero_url)
        xml_parse = etree.parse(page)
        page.close()
        root = xml_parse.getroot()
        return {'items' : root.xpath('./atom:entry', namespaces=NS),
                'count' : root.xpath('./zot:totalResults', namespaces=NS)[0].text}
    except HTTPError, error:
        error_content = error.read()
        raise Exception(error_content)
