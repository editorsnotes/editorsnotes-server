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
    max_count = 6
    object_urls = set()
    object_ids = { 'topic': [], 'note': [], 'source': [], 'transcript': [] }
    o = {}
    o['user_activity'] = []
    for entry in LogEntry.objects.select_related('content_type__name').filter(
        content_type__app_label='main',
        content_type__model__in=object_ids.keys(),
        user=request.user):
        if entry.object_id in object_ids[entry.content_type.name]:
            continue
        object_ids[entry.content_type.name].append(entry.object_id)
        try:
            obj = entry.get_edited_object()
        except ObjectDoesNotExist:
            continue
        object_url = obj.get_absolute_url().split('#')[0]
        if object_url in object_urls:
            continue
        object_urls.add(object_url)
        o['user_activity'].append({ 'what': obj, 'when': entry.action_time })
        if len(o['user_activity']) == max_count:
            break
    for model in [Topic, Note, Source]:
        model_name = model._meta.module_name
        listname = '%s_list' % model_name
        o[listname] = list(model.objects.exclude(
            id__in=object_ids[model_name]).order_by(
            '-last_updated')[:max_count])
    transcript_list = list(Transcript.objects.select_related(
            'source').exclude(id__in=object_ids['transcript']).order_by(
            '-last_updated')[:max_count])
    o['source_list'] = sorted(o['source_list'] + transcript_list,
                              key=lambda x: x.last_updated, 
                              reverse=True)[:max_count]
    return render_to_response(
        'index.html', o, context_instance=RequestContext(request))

@login_required
def all_topics(request):
    o = {}
    o['topics_1'] = []
    o['topics_2'] = []
    o['topics_3'] = []
    all_topics = list(Topic.objects.all())
    prev_letter = 'A'
    topic_index = 1
    list_index = 1 
    for topic in all_topics:
        first_letter = topic.slug[0].upper()
        if not first_letter == prev_letter:
            if topic_index > (len(all_topics) / 3.0):
                topic_index = 1
                list_index += 1
            prev_letter = first_letter
        o['topics_%s' % list_index].append(
            { 'topic': topic, 'first_letter': first_letter })
        topic_index += 1
    return render_to_response(
        'all-topics.html', o, context_instance=RequestContext(request))

@login_required
def all_sources(request):
    pass

@login_required
def all_notes(request):
    pass

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
    o['thread'] = { 'id': 'topic-%s' % o['topic'].id, 'title': o['topic'].preferred_name }
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
def footnote(request, footnote_id):
    o = {}
    o['footnote'] = get_object_or_404(Footnote, id=footnote_id)
    o['thread'] = { 'id': 'footnote-%s' % o['footnote'].id, 
                    'title': o['footnote'].footnoted_text() }
    return render_to_response(
        'footnote.html', o, context_instance=RequestContext(request))

@login_required
def source(request, source_id):
    o = {}
    o['source'] = get_object_or_404(Source, id=source_id)
    o['related_topics'] =[ c.content_object for c in o['source'].citations.filter(
            content_type=ContentType.objects.get_for_model(Topic)) ]
    o['scans'] = o['source'].scans.all()
    o['domain'] = Site.objects.get_current().domain
    notes = [ c.content_object for c in o['source'].citations.filter(
            content_type=ContentType.objects.get_for_model(Note)) ]
    o['notes'] = zip(notes, 
                     [ [ ta.topic for ta in n.topics.all() ] for n in notes ],
                     [ _sort_citations(n) for n in notes ])    
    return render_to_response(
        'source.html', o, context_instance=RequestContext(request))

@login_required
def user(request, username=None):
    o = {}
    if not username:
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    o['profile'] = UserProfile.get_for(user)
    o['log_entries'] = []
    object_urls = set()
    for entry in LogEntry.objects.select_related('content_type__model').filter(
        content_type__app_label='main', 
        content_type__model__in=['topic', 'note', 'source', 'transcript'], 
        user=user):
        object_url = '/%s/%s/' % (entry.content_type.model, entry.object_id)
        if object_url in object_urls: 
            continue
        object_urls.add(object_url)
        try:
            obj = entry.get_edited_object()
        except ObjectDoesNotExist:
            continue
        object_urls.add(obj.get_absolute_url())
        o['log_entries'].append(entry)
        if len(o['log_entries']) == 50: 
            break
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
