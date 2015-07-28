from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.base import RedirectView

from ..models import LegacyTopic, TopicNode


class LegacyTopicRedirectView(RedirectView):
    permanent = True
    query_string = True

    def get_redirect_url(self, topic_slug):
        legacy_topic = get_object_or_404(LegacyTopic, slug=topic_slug)
        return reverse('topic_node_view', args=(legacy_topic.merged_into_id,))


def topic_node(request, topic_node_id):
    o = {}
    node_qs = TopicNode.objects.select_related()
    o['topic_node'] = get_object_or_404(node_qs, id=topic_node_id)
    return render_to_response(
        'topic_node.html', o, context_instance=RequestContext(request))
