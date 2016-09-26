import random

CHARS = 'abcdefghijkmnpqrstuvwxyz3456789'
CURSE_CHARS = 'csfhuit'
NO_CURSE_CHARS = list(set(CHARS).difference(set(CURSE_CHARS)))

__all__ = ['randomish_id']

def randomish_id(length=6):
    s = ''

    # Algorithm for avoiding English curse words taken from Hashids
    # (<http://hashids.org>).
    for _ in range(length):
        choices = NO_CURSE_CHARS if s[-1:] in CURSE_CHARS else CHARS
        s += random.choice(choices)

    return s
