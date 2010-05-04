# -*- coding: utf-8 -*-

from haystack import site
from haystack.indexes import *
from models import Note

class NoteIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

site.register(Note, NoteIndex)
