# -*- coding: utf-8 -*-

from haystack import site
from haystack.indexes import *
from models import Document, Transcript, Footnote, Topic, Note

class DocumentIndex(SearchIndex):
    title = CharField(model_attr='as_text')
    text = CharField(document=True, use_template=True)

class TranscriptIndex(SearchIndex):
    title = CharField(model_attr='as_text')
    text = CharField(document=True, use_template=True)

class FootnoteIndex(SearchIndex):
    title = CharField(model_attr='as_text')
    text = CharField(document=True, use_template=True)

class TopicIndex(SearchIndex):
    title = CharField(model_attr='as_text')
    text = CharField(document=True, use_template=True)
    names = CharField(use_template=True)

class NoteIndex(SearchIndex):
    title = CharField(model_attr='as_text')
    text = CharField(document=True, use_template=True)


site.register(Document, DocumentIndex)
site.register(Transcript, TranscriptIndex)
site.register(Footnote, FootnoteIndex)
site.register(Topic, TopicIndex)
site.register(Note, NoteIndex)
