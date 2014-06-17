from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from editorsnotes.main.models import Document, Transcript
from editorsnotes.api.serializers import DocumentSerializer

from common import BaseAdminView, BootstrappedBackboneView
from .. import forms

class DocumentAdminView(BootstrappedBackboneView):
    model = Document
    serializer_class = DocumentSerializer
    def get_object(self, document_id=None):
        return document_id and get_object_or_404(
            Document, id=document_id, project_id=self.project.id)
    def get_breadcrumb(self):
        breadcrumbs = (
            (self.project.name, self.project.get_absolute_url()),
            ('Documents', reverse('all_documents_view',
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

class TranscriptAdminView(BaseAdminView):
    model = Transcript
    form_class = forms.TranscriptForm
    formset_classes = (
        forms.FootnoteFormset,
    )
    template_name = 'transcript_admin.html'
    def get(self, request, *args, **kwargs):
        response = super(TranscriptAdminView, self).get(request, *args, **kwargs)

        if isinstance(response, HttpResponseForbidden):
            return response

        footnote_fs = response.context_data['formsets']['footnote']
        if hasattr(self, 'object') and self.object is not None:
            footnote_ids = self.object.get_footnote_href_ids()
        else:
            footnote_ids = []

        footnote_fs.forms.sort(key=lambda fn: footnote_ids.index(fn.instance.id)
                               if fn.instance.id in footnote_ids else 9999)

        return response
    def get_object(self, document_id):
        self.document = get_object_or_404(
            Document, id=document_id, project_id=self.project.id)
        return self.document.transcript if self.document.has_transcript() else None
    def set_additional_object_properties(self, obj, form):
        obj.document = self.document
        return obj
    def save_object(self, form, formsets):
        obj = form.save(commit=False)
        action = 'add' if not obj.id else 'change'
        if action == 'add':
            obj.creator = self.request.user
            obj.document = self.document
        obj.last_updater = self.request.user
        obj.save()
        return obj, action
    def save_footnote_formset_form(self, form):
        footnote = form.save(commit=False)
        transcript = self.object
        stamp = form.cleaned_data.get('stamp', None)

        if not footnote.id:
            footnote.transcript = transcript
            footnote.creator = self.request.user
        footnote.last_updater = self.request.user
        footnote.save()

        if stamp:
            a = transcript.content.cssselect('a.footnote[href$="%s"]' % stamp)[0]
            a.attrib['href'] = footnote.get_absolute_url()
            transcript.save()
