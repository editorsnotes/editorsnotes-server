# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import reversion

from editorsnotes.main.models import Note

from .. import forms
from common import BaseAdminView

class NoteAdminView(BaseAdminView):
    model = Note
    form_class = forms.NoteForm
    formset_classes = (
        forms.common.TopicAssignmentFormset,
    )
    template_name = 'note_admin.html'
    def get_object(self, note_id=None):
        return note_id and get_object_or_404(
            Note, id=note_id, project_id=self.project.id)
    def get_breadcrumb(self):
        breadcrumbs = (
            (self.project.name, self.project.get_absolute_url()),
            ('Notes', reverse('all_notes_view',
                               kwargs={'project_slug': self.project.slug})),
        )
        if self.object is None:
            breadcrumbs += (
                ('Add', None),
            )
        else:
            breadcrumbs += (
                (self.object.as_text(), self.object.get_absolute_url()),
                ('Edit', None)
            )
        return breadcrumbs
    def get_form(self, form_class):
        form = form_class(**self.get_form_kwargs())
        form.fields['assigned_users'].queryset = self.project.members.all()
        return form
    def save_formset_form(self, form):
        obj = form.save(commit=False)
        obj.note = self.object
        obj.creator = self.request.user
        obj.save()
