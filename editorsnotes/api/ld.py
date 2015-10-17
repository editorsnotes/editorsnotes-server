ROOT_NAMESPACE = 'https://workingnotes.org/v#'

CONTEXT = {
    'access': {
        '@id': 'http://purl.org/dc/terms/accessRights',
        '@type': '@id'
    },
    'display_name': 'http://schema.org/name',
    'last_updated': {
        '@id': 'http://schema.org/dateModified',
        '@type': 'http://www.w3.org/2001/XMLSchema#dateTimeStamp'
    },
    'license': 'http://schema.org/license',
    'markup': {
        '@id': 'http://schema.org/text',
        '@type': 'http://www.w3.org/2001/XMLSchema#string'
    },
    'markup_html': {
        '@id': 'http://schema.org/text',
        '@type': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#HTML'
    },
    'name': 'http://schema.org/name',
    'project': 'http://schema.org/isPartOf',
    'referenced_by': {
        '@reverse': 'http://schema.org/mentions',
        '@type': '@id'
    },
    'references': {
        '@id': 'http://schema.org/mentions',
        '@type': '@id'
    },
    'related_topics': {
        '@id': 'http://schema.org/about',
        '@type': '@id'
    },
    'status': {
        '@id': 'http://spi-fm.uca.es/spdef/models/genericTools/itm/1.0#status',
        '@type': '@id'
    },
    'title': 'http://schema.org/name',
    'type': '@type',
    'updaters': {
        '@id': 'http://schema.org/author',
        '@type': '@id'
    },
    'url': '@id',
    '_embedded': {
        '@id': '@graph',
        '@container': '@index'
    },
}
