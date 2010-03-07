from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from models import Term, Reference

def index(request):
    return HttpResponse('Hello, world.')

def term(request, slug):
    o = {}
    o['contact'] = { 'name': settings.ADMINS[0][0], 
                     'email': settings.ADMINS[0][1] }
    o['term'] = Term.objects.get(slug=slug)
    o['note_list'] = o['term'].note_set.filter(type__exact='N')
    o['query_list'] = o['term'].note_set.filter(type__exact='Q')
    o['reference_list'] = Reference.objects.filter(note__in=o['note_list'])
    for note in list(o['note_list']) + list(o['query_list']):
        if ('last_updated' not in o) or (note.last_updated > o['last_updated']):
                o['last_updated'] = note.last_updated
                o['last_updater'] = note.last_updater.username
                o['last_updated_display'] = note.last_updated_display()
    return render_to_response('term.html', o)
    
