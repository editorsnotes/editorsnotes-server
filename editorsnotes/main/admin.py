from models import Note, Reference, Term, Alias, TermAssignment
from django.contrib import admin

class ReferenceInline(admin.StackedInline):
    model = Reference
    extra = 1

class TermAssignmentInline(admin.StackedInline):
    model = TermAssignment
    extra = 3

class AliasInline(admin.StackedInline):
    model = Alias
    extra = 3

class NoteAdmin(admin.ModelAdmin):
    inlines = (ReferenceInline, TermAssignmentInline)
    def save_model(self, request, note, form, change):
        if not change: # adding new note
            note.creator = request.user
        note.save()
    class Media:
        js = ('http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js', 
              'wymeditor/jquery.wymeditor.pack.js',
              'wymeditor_init.js')

class TermAdmin(admin.ModelAdmin):
    inlines = (AliasInline,)
    def save_model(self, request, term, form, change):
        if not change: # adding new term
            term.creator = request.user
        term.save()

admin.site.register(Note, NoteAdmin)
admin.site.register(Term, TermAdmin)
