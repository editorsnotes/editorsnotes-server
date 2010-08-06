from models import *
from django import forms
from django.contrib import admin
from django.db import IntegrityError
from reversion.admin import VersionAdmin

class FootnoteAdminForm(forms.ModelForm):
    stamp = forms.CharField(required=False, widget=forms.HiddenInput)
    class Meta:
        model = Footnote

class CitationInline(admin.StackedInline):
    model = Citation
    extra = 0

class TopicAssignmentInline(admin.StackedInline):
    model = TopicAssignment
    extra = 1

class AliasInline(admin.StackedInline):
    model = Alias
    extra = 0

class FootnoteInline(admin.StackedInline):
    model = Footnote
    extra = 0
    template = 'admin/edit_inline/footnote.html'
    form = FootnoteAdminForm

class ScanInline(admin.StackedInline):
    model = Scan

class NoteAdmin(VersionAdmin):
    inlines = (CitationInline, TopicAssignmentInline)
    list_display = ('excerpt', 'type', 'last_updater', 'last_updated_display')
    readonly_fields = ('edit_history',)
    def save_model(self, request, note, form, change):
        if not change: # adding new note
            note.creator = request.user
        note.last_updater = request.user
        note.save()
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances: # citations and topic assignments
            instance.creator = request.user
            instance.save()
        formset.save_m2m()
    class Media:
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin.js')

class SourceAdmin(admin.ModelAdmin):
    inlines = (ScanInline,)
    list_display = ('__unicode__', 'type', 'creator', 'created_display')
    def save_model(self, request, source, form, change):
        if not change: # adding new source
            source.creator = request.user
        source.save()
    def save_formset(self, request, form, formset, change):
        scans = formset.save(commit=False)
        for scan in scans:
            scan.creator = request.user
            scan.save()
        formset.save_m2m()

class TranscriptAdmin(admin.ModelAdmin):
    inlines = (FootnoteInline,)
    list_display = ('__unicode__', 'creator', 'created_display')
    def save_model(self, request, transcript, form, change):
        if not change: # adding new transcript
            transcript.creator = request.user
        transcript.save()
    def save_formset(self, request, form, formset, change):
        footnotes = formset.save(commit=False)
        for footnote in footnotes: # footnotes
            footnote.creator = request.user
            footnote.save()
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

class TopicAdmin(admin.ModelAdmin):
    inlines = (AliasInline,)
    def save_model(self, request, topic, form, change):
        if not change: # adding new topic
            topic.creator = request.user
        topic.save()
        if topic.article and not topic.article.has_topic(topic):
            TopicAssignment.objects.create(note=topic.article, topic=topic, creator=request.user)
    def save_formset(self, request, form, formset, change):
        aliases = formset.save(commit=False)
        for alias in aliases:
            alias.creator = request.user
            alias.save()

admin.site.register(Note, NoteAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Transcript, TranscriptAdmin)
admin.site.register(Topic, TopicAdmin)
