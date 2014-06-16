# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from editorsnotes.main.models import Note
from editorsnotes.api.serializers import NoteSerializer

from common import BootstrappedBackboneView

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
