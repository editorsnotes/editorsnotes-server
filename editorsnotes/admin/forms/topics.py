from django import forms
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.forms import models, ValidationError

from editorsnotes.main.models import Topic, TopicNode, AlternateName, Citation
from editorsnotes.main.models.topics import TYPE_CHOICES

TYPE_OPTIONS = (('', ''),) + TYPE_CHOICES

class TopicForm(models.ModelForm):
    topic_type = models.ChoiceField(choices=TYPE_OPTIONS, required=False)
    class Media:
        js = (
            "function/admin-bootstrap-topic.js",
        )
    class Meta:
        model = Topic
        fields = ('preferred_name', 'topic_type', 'summary',)
        widgets = {
            'topic': forms.HiddenInput()
        }

AlternateNameFormset = models.inlineformset_factory(
    Topic, AlternateName, fields=('name',), extra=1)

class CitationForm(models.ModelForm):
    class Meta:
        model = Citation
        fields = ('document', 'notes', 'ordering',)
        widgets = {
            'document': forms.widgets.HiddenInput(),
            'ordering': forms.widgets.HiddenInput()
        }

CitationFormset = generic_inlineformset_factory(
    Citation, form=CitationForm, extra=1)
