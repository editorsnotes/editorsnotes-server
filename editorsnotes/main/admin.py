from models import *
from django import forms
from django.contrib import admin, messages
from django.contrib.contenttypes import generic
from django.db import IntegrityError
from django.http import HttpResponseRedirect
import reversion

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

class VersionAdmin(reversion.admin.VersionAdmin):
    def save_model(self, request, obj, form, change):
        if not change: # adding new object
            obj.creator = request.user
        obj.last_updater = request.user
        obj.save()
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.creator = request.user
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
    def delete_view(self, request, object_id, extra_context=None):
        response = super(VersionAdmin, self).delete_view(request, object_id, extra_context)
        if request.POST.has_key('_return_to'):
            return HttpResponseRedirect(request.POST['_return_to'])
        else:
            return response
    def message_user(self, request, message):
        if 'success' in message.lower(): 
            messages.success(request, message)
        else:
            messages.info(request, message)
    class Media:
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin.js')

class TopicAdmin(VersionAdmin):
    inlines = (AliasInline, CitationInline)

class NoteAdmin(VersionAdmin):
    inlines = (CitationInline, TopicAssignmentInline)
    list_display = ('excerpt', 'last_updater', 'last_updated_display')
    readonly_fields = ('edit_history',)

################################################################################

class ModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change: # adding new object
            obj.creator = request.user
        obj.save()
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.creator = request.user
            instance.save()
        formset.save_m2m()
    def response_add(self, request, obj, post_url_continue='../%s/'):
        response = super(ModelAdmin, self).response_add(request, obj, post_url_continue)
        if (request.POST.has_key('_continue') or 
            request.POST.has_key('_popup') or 
            request.POST.has_key('_addanother')):
            return response
        else:
            return HttpResponseRedirect(obj.get_absolute_url())
    def response_change(self, request, obj):
        response = super(ModelAdmin, self).response_change(request, obj)
        if request.POST.has_key('_return_to') and not (
            request.POST.has_key('_continue') or 
            request.POST.has_key('_saveasnew') or 
            request.POST.has_key('_addanother')):
            return HttpResponseRedirect(request.POST['_return_to'])
        else:
            return response
    def delete_view(self, request, object_id, extra_context=None):
        response = super(ModelAdmin, self).delete_view(request, object_id, extra_context)
        if request.POST.has_key('_return_to'):
            return HttpResponseRedirect(request.POST['_return_to'])
        else:
            return response
    def message_user(self, request, message):
        if 'success' in message.lower(): 
            messages.success(request, message)
        else:
            messages.info(request, message)

class SourceAdmin(ModelAdmin):
    inlines = (ScanInline,)
    list_display = ('__unicode__', 'type', 'creator', 'created_display')
    class Media:
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin.js')

class TranscriptAdmin(ModelAdmin):
    inlines = (FootnoteInline,)
    list_display = ('__unicode__', 'creator', 'created_display')
    def save_formset(self, request, form, formset, change):
        super(TranscriptAdmin, self).save_formset(request, form, formset, change)
        transcript = form.instance
        for footnote_form in formset.forms:
            stamp = footnote_form.cleaned_data['stamp']
            if stamp:
                a = transcript.content.cssselect('a.footnote[href="' + stamp + '"]')[0]
                a.attrib['href'] = footnote_form.instance.get_absolute_url()
        transcript.save()
    class Media:
        css = { 'all': ('style/admin-transcript.css',) }
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin-transcript.js')

admin.site.register(Topic, TopicAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Transcript, TranscriptAdmin)

