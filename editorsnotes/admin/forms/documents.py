# -*- coding: utf-8 -*-

from django import forms
from django.forms.models import ModelForm, inlineformset_factory

from editorsnotes.main.models import Transcript, Footnote

class TranscriptForm(ModelForm):
    class Media:
        js = (
            'function/admin-bootstrap-transcript.js',
        )
    class Meta:
        model = Transcript
        fields = ('content',)

class FootnoteForm(ModelForm):
    class Meta:
        model = Footnote
        fields = ('content',)
    stamp = forms.CharField(required=False, widget=forms.HiddenInput)

FootnoteFormset = inlineformset_factory(
    Transcript, Footnote, form=FootnoteForm, extra=1)


