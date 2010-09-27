from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
#from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from haystack.query import SearchQuerySet, EmptySearchQuerySet
from urllib import urlopen
from models import *
import utils
import json

def _sort_citations(instance):
    cites = { 'primary': [], 'secondary': [] }
    for c in Citation.objects.filter(
        content_type=ContentType.objects.get_for_model(instance), 
        object_id=instance.id):
        if c.source.type == 'P': cites['primary'].append(c)
        elif c.source.type == 'S': cites['secondary'].append(c)
    cites['primary'].sort(key=lambda c: c.source.ordering)
    cites['secondary'].sort(key=lambda c: c.source.ordering)
    return cites

@login_required
def index(request):
    o = {}
    topics = list(Topic.objects.all())
    index = (len(topics) / 2)  + 1 
    o['source_list'] = sorted([ t.source for t in Transcript.objects.all() ], key=lambda s: s.ordering)
    o['topic_list_1'] = topics[:index]
    o['topic_list_2'] = topics[index:]
    o['activity'] = []
    prev_obj = None
    for entry in LogEntry.objects.filter(content_type__app_label='main')[:20]:
        try:
            obj = entry.get_edited_object()
        except ObjectDoesNotExist:
            continue
        if obj == prev_obj: continue
        e = {}
        e['action'] = entry.action_flag
        e['who'] = entry.user
        if entry.content_type.name == 'topic':
            e['what'] = '<a href="%s">%s</a>' % (obj.get_absolute_url(), obj)
        elif entry.content_type.name == 'source':
            e['what'] = '<a href="%s">%s</a>' % (obj.get_absolute_url(), obj)
        elif entry.content_type.name == 'transcript':
            e['what'] = '<a href="%s">the transcript of %s</a>' % (obj.get_absolute_url(), obj.source)
        elif entry.content_type.name == 'note':
            e['what'] = '<a href="%s">a note</a>' % obj.get_absolute_url()
            topics = [ ('<a class="subtle" href="%s">%s</a>' % (ta.topic.get_absolute_url(), ta.topic.preferred_name)) 
                       for ta in obj.topics.all() ]
            if len(topics) > 0:
                e['what'] += ' about '
                if len(topics) == 1:
                    e['what'] += topics[0]
                elif len(topics) == 2:
                    e['what'] += ' and '.join(topics)
                else:
                    e['what'] += (', '.join(topics[:-1]) + ', and ' + topics[-1])
        else:
            e['what'] = '<a href="%s">a %s</a>' % (obj.get_absolute_url(), entry.content_type.name)
        e['when'] = utils.timeago(entry.action_time)
        o['activity'].append(e)
        prev_obj = obj
    return render_to_response(
        'index.html', o, context_instance=RequestContext(request))

@login_required
def topic(request, topic_slug):
    o = {}
    o['topic'] = get_object_or_404(Topic, slug=topic_slug)
    o['contact'] = { 'name': settings.ADMINS[0][0], 
                     'email': settings.ADMINS[0][1] }
    o['related_topics'] = o['topic'].related_topics.all()
    o['summary_cites'] = _sort_citations(o['topic'])
    notes = [ ta.content_object for ta in o['topic'].assignments.filter(
           content_type=ContentType.objects.get_for_model(Note)) ]
    o['notes'] = zip(notes, 
                    [ [ ta.topic for ta in n.topics.exclude(topic=o['topic']) ] for n in notes ],
                    [ _sort_citations(n) for n in notes ])
    return render_to_response(
        'topic.html', o, context_instance=RequestContext(request))

@login_required
def note(request, note_id):
    o = {}
    o['note'] = get_object_or_404(Note, id=note_id)
    o['cites'] = _sort_citations(o['note'])
    return render_to_response(
        'note.html', o, context_instance=RequestContext(request))

@login_required
def source(request, source_id):
    o = {}
    o['source'] = get_object_or_404(Source, id=source_id)
    o['scans'] = o['source'].scans.all()
    o['domain'] = Site.objects.get_current().domain
    return render_to_response(
        'source.html', o, context_instance=RequestContext(request))

@login_required
def transcript(request, transcript_id):
    o = {}
    o['transcript'] = get_object_or_404(Transcript, id=transcript_id)
    o['notes'] = o['transcript'].footnotes.all()
    return render_to_response(
        'transcript.html', o, context_instance=RequestContext(request))

@login_required
def user(request, username=None):
    o = {}
    if not username:
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    o['profile'] = UserProfile.get_for(user)
    o['notes'] = Note.objects.filter(Q(creator=user) | Q(last_updater=user))
    return render_to_response(
        'user.html', o, context_instance=RequestContext(request))

@login_required
def search(request):
    query = ''
    results = EmptySearchQuerySet()

    if request.GET.get('q'):
        query = request.GET.get('q')
        results = SearchQuerySet().auto_query(query).load_all()

    # paginator = Paginator(results, 20)
    
    # try:
    #     page = paginator.page(int(request.GET.get('page', 1)))
    # except InvalidPage:
    #     raise Http404('No such page of results!')
    
    o = {
        # 'page': page,
        # 'paginator': paginator,
        'results': results,
        'query': query,
    }
    
    return render_to_response(
        'search.html', o, context_instance=RequestContext(request))

def api_topics(request):
    query = ''
    results = EmptySearchQuerySet()

    if request.GET.get('q'):
        query = ' AND '.join([ 'names:%s' % term for term 
                               in request.GET.get('q').split() 
                               if len(term) > 1 ])
        results = SearchQuerySet().models(Topic).narrow(query).load_all()
    
    topics = [ { 'preferred_name': r.object.preferred_name,
                 'uri': 'http://%s%s' % (Site.objects.get_current().domain, 
                                         r.object.get_absolute_url()) } 
               for r in results ]
    return HttpResponse(json.dumps(topics), mimetype='text/plain')

# Proxy for cross-site AJAX requests. For development only.
def proxy(request):
    url = request.GET.get('url')
    if url is None:
        return HttpResponseBadRequest()
    if not url.startswith('http://cache.zoom.it/'):
        return HttpResponseForbidden()
    return HttpResponse(urlopen(url).read(), mimetype='application/xml')
