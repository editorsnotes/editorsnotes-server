import re
from urlparse import urlparse

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest


SPECIAL_CHARS = re.compile('([+\-&|!(){}\[\]^~*?:/])')


def clean_query_string(query):
    # Strip any backslashes
    cleaned = query.replace('\\', '')

    # Remove special characters
    cleaned = re.sub(SPECIAL_CHARS, r'\\\1', cleaned)

    # Remove unbalanced quotations
    cleaned = re.sub('((?:"[^"]*?"[^"]*?)*?)"?([^"]*$)', r'\1\2', cleaned)

    return cleaned


def make_dummy_request():
    base_url = settings.ELASTICSEARCH_SITE
    parsed = urlparse(base_url)

    secure = parsed.scheme is 'https'
    hostname = parsed.hostname
    port = parsed.port or (443 if secure else 80)

    request = WSGIRequest({
        'REQUEST_METHOD': 'GET',
        'wsgi.input': '',
        'SERVER_NAME': hostname,
        'SERVER_PORT': port
    })
    if secure:
        request._is_secure = lambda: True
    return request
