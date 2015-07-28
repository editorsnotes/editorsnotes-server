from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from ..models import Footnote, Transcript


def transcript(request, project_slug, document_id):
    transcript = get_object_or_404(Transcript, document_id=document_id)
    return HttpResponse(transcript)


def footnote(request, project_slug, document_id, footnote_id):
    o = {}
    o['footnote'] = get_object_or_404(Footnote, id=footnote_id)
    o['thread'] = {
        'id': 'footnote-%s' % o['footnote'].id,
        'title': o['footnote'].footnoted_text()
    }
    return render_to_response(
        'footnote.html', o, context_instance=RequestContext(request))
