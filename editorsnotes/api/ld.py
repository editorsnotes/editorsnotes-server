from collections import OrderedDict


ROOT_NAMESPACE = 'https://workingnotes.org/v#'


NAMESPACES = OrderedDict((
    ('dc', 'http://purl.org/dc/terms/'),
    ('hydra', 'http://www.w3.org/ns/hydra/core#'),
    ('itm', 'http://spi-fm.uca.es/spdef/models/genericTools/itm/1.0#'),
    ('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
    ('rdfs', 'http://www.w3.org/2000/01/rdf-schema#'),
    ('schema', 'http://schema.org/'),
    ('vaem', 'http://www.linkedmodel.org/schema/vaem#'),
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
    ('aspects', 'vaem:hasAspect'),
    ('data', OrderedDict((
        ('@id', '@graph'),
        ('@container', '@index'),
    ))),
    ('display_name', 'schema:name'),
    ('domain', OrderedDict((
        ('@id', 'rdfs:domain'),
        ('@type', '@id'),
    ))),
    ('embedded', OrderedDict((
        ('@id', '@graph'),
        ('@container', '@index'),
    ))),
    ('last_updated', OrderedDict((
        ('@id', 'schema:dateModified'),
        ('@type', 'xsd:dateTimeStamp'),
    ))),
    ('label', 'rdfs:label'),
    ('license', 'schema:license'),
    ('linked_data', OrderedDict((
        ('@container', '@index'),
        ('@id', 'vaem:hasAspect'),
    ))),
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
    ('range', OrderedDict((
        ('@id', 'rdfs:range'),
        ('@type', '@id'),
    ))),
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
    ('wn_data', OrderedDict((
        ('@container', '@index'),
        ('@id', 'vaem:hasAspect'),
    ))),
)))
