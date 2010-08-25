# -*- coding: utf-8 -*-

from haystack import site
from haystack.indexes import *
from models import Note, Topic, Source

class NoteIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

class TopicIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

class SourceIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

site.register(Note, NoteIndex)
site.register(Topic, TopicIndex)
site.register(Source, SourceIndex)
