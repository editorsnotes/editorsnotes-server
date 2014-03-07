# -*- coding: utf-8 -*-

from django import forms
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.forms.models import ModelForm
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe

from editorsnotes.main.models.topics import Topic, TopicAssignment

class TopicAssignmentWidget(forms.widgets.HiddenInput):
    def render(self, name, value, attrs=None):
        hidden_input = super(TopicAssignmentWidget, self).render(name, value, attrs=None)
        if value:
            topic = get_object_or_404(Topic, id=value)
            extra_content = topic.preferred_name
        else:
            extra_content = ''
        return mark_safe(extra_content + hidden_input)

class TopicAssignmentForm(ModelForm):
    topic_id = forms.IntegerField(widget=TopicAssignmentWidget)
    class Meta:
        model = TopicAssignment
        fields = ('topic_id',)
    def __init__(self, *args, **kwargs):
        super(TopicAssignmentForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.id:
            self.fields['topic_id'].initial = self.instance.topic.id
    def clean_topic_id(self):
        data = self.cleaned_data['topic_id']
        if self.instance and self.instance.id:
            return data
        # If this is a new object, the "topic_id" is actually the
        # "topic_node_id". This is hacky and will be removed when we eventually
        # create interfaces for editing anything with the API
        topic_qs = Topic.objects.filter(topic_node_id=data)
        if not topic_qs.exists():
            raise forms.ValidationError('This topic does not exist.')
        self.cleaned_data['topic_qs'] = topic_qs
        return data

TopicAssignmentFormset = generic_inlineformset_factory(
    TopicAssignment, form=TopicAssignmentForm, extra=1)
