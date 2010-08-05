from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from models import Topic, Note, Transcript, UserProfile
from django.db.models import Q

def _sort_citations(note):
    cites = { 'primary': [], 'secondary': [] }
    for c in note.citations.all():
        if c.source.type == 'P': cites['primary'].append(c)
        elif c.source.type == 'S': cites['secondary'].append(c)
    return cites

@login_required
def index(request):
    o = {}
    o['topic_list'] = Topic.objects.all()
    return render_to_response('index.html', o)

@login_required
def topic(request, topic_slug):
    o = {}
    o['topic'] = get_object_or_404(Topic, slug=topic_slug)
    o['contact'] = { 'name': settings.ADMINS[0][0], 
                     'email': settings.ADMINS[0][1] }
    notes = list(o['topic'].note_set.filter(type='N'))
    queries = list(o['topic'].note_set.filter(type='Q'))
    if o['topic'].article:
        o['article'] = o['topic'].article
        if o['article'] in notes: 
            notes.remove(o['article'])
        if o['article'] in queries:
            queries.remove(o['article'])
    o['notes'] = zip(notes, [ _sort_citations(n) for n in notes ])
    o['queries'] = zip(queries, [ _sort_citations(q) for q in queries ])
    last_updated_note = None
    for note in notes + queries:
        if (not last_updated_note) or (note.last_updated > last_updated_note.last_updated):
            last_updated_note = note
    if last_updated_note:
        o['last_updated_display'] = last_updated_note.last_updated_display()
        o['last_updater_display'] = UserProfile.get_for(last_updated_note.last_updater).name_display()
    else:
        o['created_display'] = o['topic'].created_display()
        o['creator_display'] = UserProfile.get_for(o['topic'].creator).name_display()
    return render_to_response('topic.html', o)

@login_required
def note(request, note_id):
    o = {}
    o['note'] = get_object_or_404(Note, id=note_id)
    o['cites'] = _sort_citations(o['note'])
    return render_to_response('note.html', o)

@login_required
def transcript(request, transcript_id):
    o = {}
    o['transcript'] = get_object_or_404(Transcript, id=transcript_id)
    o['notes'] = o['transcript'].footnotes.all()
    return render_to_response('transcript.html', o)

@login_required
def user(request, username=None):
    o = {}
    if not username:
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    o['profile'] = UserProfile.get_for(user)
    o['notes'] = Note.objects.filter(Q(creator=user) | Q(last_updater=user))
    return render_to_response('user.html', o)
    
