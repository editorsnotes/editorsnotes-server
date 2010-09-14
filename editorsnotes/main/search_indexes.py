# -*- coding: utf-8 -*-

from haystack import site
from haystack.indexes import *
from models import Note, Topic, Source

class NoteIndex(SearchIndex):
    title = CharField(model_attr='title')
    text = CharField(document=True, use_template=True)

class TopicIndex(SearchIndex):
    title = CharField(model_attr='preferred_name')
    text = CharField(document=True, use_template=True)
    names = CharField(use_template=True)

class SourceIndex(SearchIndex):
    title = CharField(model_attr='description_as_text')
    text = CharField(document=True, use_template=True)

site.register(Note, NoteIndex)
site.register(Topic, TopicIndex)
site.register(Source, SourceIndex)
