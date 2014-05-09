# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from editorsnotes.main.models import Note
from editorsnotes.api.serializers import NoteSerializer

from .. import forms
from common import BaseAdminView, BootstrappedBackboneView

class NoteAdminView(BootstrappedBackboneView):
    model = Note
    serializer_class = NoteSerializer
    def get_object(self, note_id=None):
        return note_id and get_object_or_404(
            Note, id=note_id, project_id=self.project.id)
    def get_breadcrumb(self):
        breadcrumbs = (
            (self.project.name, self.project.get_absolute_url()),
            ('Notes', reverse('all_notes_view', kwargs={'project_slug': self.project.slug})),
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

class OldNoteAdminView(BaseAdminView):
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
