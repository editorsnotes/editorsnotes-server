from collections import OrderedDict


ROOT_NAMESPACE = 'https://workingnotes.org/v#'


NAMESPACES = OrderedDict((
    ('dc', 'http://purl.org/dc/terms/'),
    ('hydra', 'http://www.w3.org/ns/hydra/core#'),
    ('itm', 'http://spi-fm.uca.es/spdef/models/genericTools/itm/1.0#'),
    ('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
    ('schema', 'http://schema.org/'),
    ('xsd', 'http://www.w3.org/2001/XMLSchema#'),
    ('wn', ROOT_NAMESPACE),
))


CONTEXT = NAMESPACES.copy()
CONTEXT.update(OrderedDict((
    ('access', OrderedDict((
        ('@id', 'dc:accessRights'),
        ('@type', '@id')
    ))),
    ('affilated_projects', OrderedDict((
        ('@id', '@graph'),
        ('@container', '@index'),
    ))),
    ('display_name', 'schame:name'),
    ('embedded', OrderedDict((
        ('@id', '@graph'),
        ('@container', '@index'),
    ))),
    ('last_updated', OrderedDict((
        ('@id', 'schema:dateModified'),
        ('@type', 'xsd:dateTimeStamp'),
    ))),
    ('license', 'schema:license'),
    ('links', OrderedDict((
        ('@id', '@graph'),
        ('@container', '@set'),
    ))),
    ('markup', OrderedDict((
        ('@id', 'schema:text'),
        ('@type', 'xsd:string'),
    ))),
    ('markup_html', OrderedDict((
        ('@id', 'schema:text'),
        ('@type', 'rdf:HTML'),
    ))),
    ('name', 'schema:name'),
    ('project', 'schema:isPartOf'),
    ('referenced_by', OrderedDict((
        ('@reverse', 'schema:mentions'),
        ('@type', '@id'),
    ))),
    ('references', OrderedDict((
        ('@id', 'schema:mentions'),
        ('@type', '@id'),
    ))),
    ('related_topics', OrderedDict((
        ('@id', 'schema:about'),
        ('@type', '@id'),
    ))),
    ('status', OrderedDict((
        ('@id', 'item:status'),
        ('@type', '@id'),
    ))),
    ('title', 'schema:name'),
    ('type', '@type'),
    ('updaters', OrderedDict((
        ('@id', 'schema:author'),
        ('@type', '@id'),
    ))),
    ('url', '@id'),
)))
