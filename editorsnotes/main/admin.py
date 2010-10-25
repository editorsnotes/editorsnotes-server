from models import *
from django import forms
from django.contrib import admin, messages
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models.fields import FieldDoesNotExist
from django.http import HttpResponseRedirect
from reversion import admin as reversion_admin
from lxml import etree

class FootnoteAdminForm(forms.ModelForm):
    stamp = forms.CharField(required=False, widget=forms.HiddenInput)
    class Meta:
        model = Footnote

class CitationInline(generic.GenericStackedInline):
    model = Citation
    extra = 0

class TopicAssignmentInline(generic.GenericStackedInline):
    model = TopicAssignment
    extra = 1

class AliasInline(admin.StackedInline):
    model = Alias
    extra = 0

class FootnoteInline(admin.StackedInline):
    model = Footnote
    extra = 0
    template = 'admin/main/footnote/edit_inline/stacked.html'
    form = FootnoteAdminForm

class ScanInline(admin.StackedInline):
    model = Scan

################################################################################

class VersionAdmin(reversion_admin.VersionAdmin):
    list_display = ('as_text', 'last_updater', 'last_updated')
    def save_model(self, request, obj, form, change):
        if not change: # adding new object
            obj.creator = request.user
        obj.last_updater = request.user
        obj.save()
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            try:
                instance.creator
            except ObjectDoesNotExist:
                instance.creator = request.user
            if 'last_updated' in instance._meta.get_all_field_names():
                instance.last_updater = request.user
            instance.save()
        formset.save_m2m()
    def response_add(self, request, obj, post_url_continue='../%s/'):
        response = super(VersionAdmin, self).response_add(request, obj, post_url_continue)
        if (request.POST.has_key('_continue') or 
            request.POST.has_key('_popup') or 
            request.POST.has_key('_addanother')):
            return response
        else:
            return HttpResponseRedirect(obj.get_absolute_url())
    def response_change(self, request, obj):
        response = super(VersionAdmin, self).response_change(request, obj)
        if request.POST.has_key('_return_to') and not (
            request.POST.has_key('_continue') or 
            request.POST.has_key('_saveasnew') or 
            request.POST.has_key('_addanother')):
            return HttpResponseRedirect(request.POST['_return_to'])
        else:
            return response
    # def delete_view(self, request, object_id, extra_context=None):
    #     response = super(VersionAdmin, self).delete_view(request, object_id, extra_context)
    #     if request.POST.has_key('_return_to'):
    #         return HttpResponseRedirect(request.POST['_return_to'])
    #     else:
    #         return response
    def message_user(self, request, message):
        if 'success' in message.lower(): 
            messages.success(request, message)
        else:
            messages.info(request, message)

class TopicAdmin(VersionAdmin):
    inlines = (AliasInline, CitationInline)
    class Media:
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin.js')

class NoteAdmin(VersionAdmin):
    inlines = (CitationInline, TopicAssignmentInline)
    class Media:
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin.js')

class DocumentAdmin(VersionAdmin):
    inlines = (ScanInline,)
    class Media:
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin.js')

class TranscriptAdmin(VersionAdmin):
    inlines = (FootnoteInline,)
    def save_formset(self, request, form, formset, change):
        transcript = form.instance
        # Update the transcript HTML to remove any links to deleted footnotes.
        for footnote_form in formset.forms:
            if formset._should_delete_form(footnote_form):
                footnote_form.instance.remove_self_from(transcript)
        # Save the transcript formset.
        super(TranscriptAdmin, self).save_formset(request, form, formset, change)
        # Update the transcript HTML with correct links to any new footnotes.
        for footnote_form in formset.forms:
            if (hasattr(footnote_form, 'cleaned_data') and 
                'stamp' in footnote_form.cleaned_data):
                stamp = footnote_form.cleaned_data['stamp']
                if stamp:
                    a = transcript.content.cssselect('a.footnote[href="' + stamp + '"]')[0]
                    a.attrib['href'] = footnote_form.instance.get_absolute_url()
        # Save the transcript HTML.
        transcript.save()
    class Media:
        css = { 'all': ('style/admin-transcript.css',) }
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin-transcript.js')

class FootnoteAdmin(VersionAdmin):
    class Media:
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin.js')

admin.site.register(Topic, TopicAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Transcript, TranscriptAdmin)
admin.site.register(Footnote, FootnoteAdmin)
