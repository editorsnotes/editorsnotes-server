from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from models import Term, Note

@login_required
def index(request):
    o = {}
    o['term_list'] = Term.objects.all()
    return render_to_response('index.html', o)

@login_required
def term(request, term_slug):
    o = {}
    o['term'] = get_object_or_404(Term, slug=term_slug)
    o['contact'] = { 'name': settings.ADMINS[0][0], 
                     'email': settings.ADMINS[0][1] }
    notes = list(o['term'].note_set.filter(type__exact='N'))
    queries = list(o['term'].note_set.filter(type__exact='Q'))
    def sort_references(note):
        refs = { 'primary': [], 'secondary': [] }
        for r in note.references.all():
            if r.type == 'P': refs['primary'].append(r)
            elif r.type == 'S': refs['secondary'].append(r)
        return refs
    o['notes'] = zip(notes, [ sort_references(n) for n in notes ])
    o['queries'] = zip(queries, [ sort_references(q) for q in queries ])
    for note in notes + queries:
        if ('last_updated' not in o) or (note.last_updated > o['last_updated']):
                o['last_updated'] = note.last_updated
                o['last_updater'] = note.last_updater.username
                o['last_updated_display'] = note.last_updated_display()
    return render_to_response('term.html', o)

@login_required
def note(request, note_id):
    o = {}
    o['note'] = get_object_or_404(Note, id=note_id)
    return render_to_response('note.html', o)
    
