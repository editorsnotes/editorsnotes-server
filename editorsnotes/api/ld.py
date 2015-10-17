from collections import OrderedDict

ROOT_NAMESPACE = 'https://workingnotes.org/v#'

CONTEXT = OrderedDict((
    ('access', OrderedDict((
        ('@id', 'http://purl.org/dc/terms/accessRights'),
        ('@type', '@id')
    ))),
    ('display_name', 'http://schema.org/name'),
    ('last_updated', OrderedDict((
        ('@id', 'http://schema.org/dateModified'),
        ('@type', 'http://www.w3.org/2001/XMLSchema#dateTimeStamp'),
    ))),
    ('license', 'http://schema.org/license'),
    ('markup', OrderedDict((
        ('@id', 'http://schema.org/text'),
        ('@type', 'http://www.w3.org/2001/XMLSchema#string'),
    ))),
    ('markup_html', OrderedDict((
        ('@id', 'http://schema.org/text'),
        ('@type', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#HTML'),
    ))),
    ('name', 'http://schema.org/name'),
    ('project', 'http://schema.org/isPartOf'),
    ('referenced_by', OrderedDict((
        ('@reverse', 'http://schema.org/mentions'),
        ('@type', '@id'),
    ))),
    ('references', OrderedDict((
        ('@id', 'http://schema.org/mentions'),
        ('@type', '@id'),
    ))),
    ('related_topics', OrderedDict((
        ('@id', 'http://schema.org/about'),
        ('@type', '@id'),
    ))),
    ('status', OrderedDict((
        ('@id', 'http://spi-fm.uca.es/spdef/models/genericTools/itm/1.0#status'),
        ('@type', '@id'),
    ))),
    ('title', 'http://schema.org/name'),
    ('type', '@type'),
    ('updaters', OrderedDict((
        ('@id', 'http://schema.org/author'),
        ('@type', '@id'),
    ))),
    ('url', '@id'),
    ('_embedded', OrderedDict((
        ('@id', '@graph'),
        ('@container', '@index'),
    )))
))
