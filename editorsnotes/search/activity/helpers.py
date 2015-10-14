"""
Functions for the activity index.
"""

import json
from collections import OrderedDict

from rest_framework.renderers import JSONRenderer

from editorsnotes.auth.models import Project, User

from .. import activity_index


def get_activity_for(entity, es_query=None, size=25):
    query = es_query or {}
    if 'size' not in query:
        query['size'] = size
    if 'sort' not in query:
        query['sort'] = {
            'data.time': {'order': 'desc', 'ignore_unmapped': True}
        }
    if 'query' not in query:
        query['query'] = {'filtered': {'filter': {'bool': {'must': []}}}}

    if isinstance(entity, User):
        query['query']['filtered']['filter']['bool']['must'].append({
            'term': {'data.user': entity.username}
        })
    elif isinstance(entity, Project):
        query['query']['filtered']['filter']['bool']['must'].append({
            'term': {'data.project': entity.slug}
        })
    else:
        raise ValueError('Must pass either project or user')

    search = activity_index.es.search(query, index=activity_index.name)
    return [hit['_source']['data'] for hit in search['hits']['hits']]


def handle_activity_edit(instance, refresh=True):
    from editorsnotes.api.serializers import ActivitySerializer

    serializer = ActivitySerializer(instance)
    data = json.loads(JSONRenderer().render(serializer.data),
                      object_pairs_hook=OrderedDict)

    activity_index.es.index(
        activity_index.name, 'activity', {'id': instance.id, 'data': data},
        refresh=refresh)
