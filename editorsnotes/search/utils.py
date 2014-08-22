import re

SPECIAL_CHARS = re.compile('([+\-&|!(){}\[\]^~*?:/])')

def clean_query_string(query):
    # Strip any backslashes
    cleaned = query.replace('\\', '')

    # Remove special characters
    cleaned = re.sub(SPECIAL_CHARS, r'\\\1', cleaned)

    # Remove unbalanced quotations
    cleaned = re.sub('((?:"[^"]*?"[^"]*?)*?)"?([^"]*$)', r'\1\2', cleaned)

    return cleaned
