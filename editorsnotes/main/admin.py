from models import Note, Source, Transcript, Footnote, Citation, Term, Alias, TermAssignment
from django import forms
from django.contrib import admin
from reversion.admin import VersionAdmin

class CitationInline(admin.StackedInline):
    model = Citation
    extra = 0

class TermAssignmentInline(admin.StackedInline):
    model = TermAssignment
    extra = 1

class AliasInline(admin.StackedInline):
    model = Alias
    extra = 0

class FootnoteAdminForm(forms.ModelForm):
    stamp = forms.CharField(required=True, widget=forms.HiddenInput)
    class Meta:
        model = Footnote

class FootnoteInline(admin.StackedInline):
    model = Footnote
    extra = 0
    template = 'admin/edit_inline/footnote.html'
    form = FootnoteAdminForm

class NoteAdmin(VersionAdmin):
    inlines = (CitationInline, TermAssignmentInline)
    list_display = ('excerpt', 'type', 'last_updater', 'last_updated_display')
    readonly_fields = ('edit_history',)
    def save_model(self, request, note, form, change):
        if not change: # adding new note
            note.creator = request.user
        note.last_updater = request.user
        note.save()
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances: # citations and term assignments
            instance.creator = request.user
            instance.save()
        formset.save_m2m()
    class Media:
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin.js')

class SourceAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'type', 'creator', 'created_display')
    def save_model(self, request, source, form, change):
        if not change: # adding new source
            source.creator = request.user
        source.save()
    class Media:
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin.js')

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
            a = transcript.content.cssselect('a.footnote[href=' + stamp + ']')[0]
            a.attrib['href'] = footnote_form.instance.get_absolute_url()
        transcript.save()
    class Media:
        css = { 'all': ('style/admin-transcript.css',) }
        js = ('function/jquery-1.4.2.min.js',
              'function/wymeditor/jquery.wymeditor.pack.js',
              'function/jquery.timeago.js',
              'function/admin-transcript.js')

class TermAdmin(admin.ModelAdmin):
    inlines = (AliasInline,)
    def save_model(self, request, term, form, change):
        if not change: # adding new term
            term.creator = request.user
        term.save()
    def save_formset(self, request, form, formset, change):
        aliases = formset.save(commit=False)
        for alias in aliases:
            alias.creator = request.user
            alias.save()

admin.site.register(Note, NoteAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Transcript, TranscriptAdmin)
admin.site.register(Term, TermAdmin)
