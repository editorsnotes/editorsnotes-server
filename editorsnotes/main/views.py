from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from models import *
from django.db.models import Q
import utils

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
    o['article_list'] = Topic.objects.filter(article__isnull=False)
    o['activity'] = []
    prev_obj = None
    for entry in LogEntry.objects.filter(content_type__app_label='main')[:10]:
        obj = entry.get_edited_object()
        if obj == prev_obj: continue
        e = {}
        e['action'] = entry.action_flag
        e['who'] = UserProfile.get_for(entry.user).name_display()
        e['what'] = '<a href="' + obj.get_absolute_url() + '">' + entry.content_type.name + '</a>'
        if entry.content_type.name == 'note':
            topics = [ ('<a class="subtle" href="' + t.get_absolute_url() + '">' + t.preferred_name + '</a>') for t in obj.topics.all() ]
            if len(topics) > 0:
                e['what'] += ' about '
                if len(topics) == 1:
                    e['what'] += topics[0]
                elif len(topics) == 2:
                    e['what'] += ' and '.join(topics)
                else:
                    e['what'] += (', '.join(topics[:-1]) + ', and ' + topics[-1])
        e['when'] = utils.timeago(entry.action_time)
        o['activity'].append(e)
        prev_obj = obj
    return render_to_response('index.html', o)

@login_required
def topic(request, topic_slug):
    o = {}
    o['topic'] = get_object_or_404(Topic, slug=topic_slug)
    o['contact'] = { 'name': settings.ADMINS[0][0], 
                     'email': settings.ADMINS[0][1] }
    o['related_articles'] = []
    for article in o['topic'].note_set.filter(main_topic__isnull=False):
        if not article.main_topic == o['topic']:
            o['related_articles'].append(article.main_topic)
    notes = list(o['topic'].note_set.filter(main_topic__isnull=True))
    if o['topic'].article:
        o['article'] = o['topic'].article
        if o['article'] in notes: 
            notes.remove(o['article'])
        o['article_topics'] = o['article'].topics.exclude(id=o['topic'].id)
        o['article_cites'] = _sort_citations(o['article'])
    o['notes'] = zip(notes, 
                     [ n.topics.exclude(id=o['topic'].id) for n in notes ],
                     [ _sort_citations(n) for n in notes ])
    return render_to_response('topic.html', o)

@login_required
def note(request, note_id):
    o = {}
    o['note'] = get_object_or_404(Note, id=note_id)
    o['cites'] = _sort_citations(o['note'])
    return render_to_response('note.html', o)

@login_required
def source(request, source_id):
    o = {}
    o['source'] = get_object_or_404(Source, id=source_id)
    o['scans'] = o['source'].scans.all()
    return render_to_response('source.html', o)

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
    
