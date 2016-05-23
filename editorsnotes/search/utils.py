import re
from urllib.parse import urlparse

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
    parsed = urlparse(settings.SITE_URL)

    request = WSGIRequest({
        'wsgi.input': '',
        'wsgi.url_scheme': parsed.scheme,
        'REQUEST_METHOD': 'GET',
        'SERVER_NAME': parsed.hostname,
        'SERVER_PORT': parsed.port or (443 if parsed.scheme == 'https' else 80)
    })

    return request
