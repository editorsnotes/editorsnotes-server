from django import forms
from django.forms.models import ModelForm, inlineformset_factory

from editorsnotes.main.models import Note, CitationNS

class NoteForm(ModelForm):
    class Media:
        js = (
            "function/admin-bootstrap-note.js",
        )
    class Meta:
        model = Note
        exclude = ('project', 'sections_counter',)
        widgets = {
            'assigned_users': forms.CheckboxSelectMultiple()
        }
