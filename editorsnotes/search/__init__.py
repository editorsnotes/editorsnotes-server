__all__ = ['get_index']

indexes = {}

def get_index(name):
    if name == 'main':
        if 'main' not in indexes:
            from .index import ENIndex
            indexes['main'] = ENIndex()
        return indexes['main']

    elif name == 'activity':
        if 'activity' not in indexes:
            from .index import ActivityIndex
            indexes['activity'] = ActivityIndex()
        return indexes['activity']

    else:
        raise ValueError('No such index: {}'.format(name))

default_app_config = 'editorsnotes.search.apps.SearchAppConfig'
