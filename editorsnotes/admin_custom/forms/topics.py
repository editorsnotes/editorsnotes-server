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
            "function/admin-bootstrap-note-sections.js",
        )
    class Meta:
        model = Topic
        fields = ('preferred_name', 'topic_type', 'topic_node',)
        widgets = {
            'topic': forms.HiddenInput()
        }
    def __init__(self, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance is not None:
            self.fields['topic_type'].initial = instance.topic.type
            self.fields['topic'] = instance.topic_node_id
    def clean_topic_node(self):
        data = self.cleaned_data['topic_node']
        if getattr(self, 'instance', None):
            if self.instance.topic_node_id != int(data):
                raise ValidationError(
                    'Topic node input can not be changed from this form. '
                    'To change the topic node, use the merge function.')
        elif data:
            if not TopicNode.objects.filter(id=data).exists():
                msg = 'TopicNode with id {} does not exist.'.format(data)
                raise ValidationError(msg)
        return data

AlternateNameFormset = models.inlineformset_factory(
    Topic, AlternateName, fields=('name',), extra=1)

class CitationForm(models.ModelForm):
    class Meta:
        model = Citation
        fields = ('document', 'notes', 'ordering',)
        widgets = {'document': forms.widgets.HiddenInput()}

CitationFormset = generic_inlineformset_factory(
    Citation, form=CitationForm, extra=1)
