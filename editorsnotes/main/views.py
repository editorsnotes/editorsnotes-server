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
    o['note_list'] = list(o['term'].note_set.filter(type__exact='N'))
    o['query_list'] = list(o['term'].note_set.filter(type__exact='Q'))
    o['note_dict'] = [ (n, n.references.all()) for n in o['note_list'] ]
    o['query_dict'] = [ (q, q.references.all()) for q in o['query_list'] ]
    for note in o['note_list'] + o['query_list']:
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
    
