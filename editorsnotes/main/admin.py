from models import Note, Reference, Term, Alias, TermAssignment
from django.contrib import admin

class ReferenceInline(admin.StackedInline):
    model = Reference
    extra = 0

class TermAssignmentInline(admin.StackedInline):
    model = TermAssignment
    extra = 1

class AliasInline(admin.StackedInline):
    model = Alias
    extra = 0

class NoteAdmin(admin.ModelAdmin):
    inlines = (ReferenceInline, TermAssignmentInline)
    list_display = ('excerpt', 'type', 'creator', 'created_display')
    readonly_fields = ('edit_history',)
    def save_model(self, request, note, form, change):
        if not change: # adding new note
            note.creator = request.user
        note.last_updater = request.user
        note.save()
    def save_formset(self, request, form, formset, change):
        term_assignments = formset.save(commit=False)
        for term_assignment in term_assignments:
            term_assignment.creator = request.user
            term_assignment.save()
        formset.save_m2m()
    class Media:
        js = ('wymeditor/jquery.wymeditor.pack.js',
              'jquery.timeago.js',
              'admin.js')

class TermAdmin(admin.ModelAdmin):
    inlines = (AliasInline,)
    def save_model(self, request, term, form, change):
        if not change: # adding new term
            term.creator = request.user
        term.save()

admin.site.register(Note, NoteAdmin)
admin.site.register(Term, TermAdmin)
