"""
Functions for the activity index.
"""

import json
from collections import OrderedDict

from rest_framework.renderers import JSONRenderer

from .. import activity_index


def handle_activity_edit(instance, refresh=True):
    from editorsnotes.api.serializers import ActivitySerializer

    serializer = ActivitySerializer(instance)
    data = json.loads(JSONRenderer().render(serializer.data),
                      object_pairs_hook=OrderedDict)

    activity_index.es.index(
        activity_index.name, 'activity', {'id': instance.id, 'data': data},
        refresh=refresh)
