# -*- coding: utf-8 -*- 

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from editorsnotes.main.models import Topic
from editorsnotes.api.serializers import TopicSerializer

from common import BootstrappedBackboneView

class TopicAdminView(BootstrappedBackboneView):
    model = Topic
    serializer_class = TopicSerializer
    def get_object(self, topic_node_id=None):
        return topic_node_id and get_object_or_404(
            Topic, topic_node_id=topic_node_id, project__slug=self.project.slug)
    def get_breadcrumb(self):
        breadcrumbs = (
            (self.project.name, self.project.get_absolute_url()),
            ('Topics', reverse('all_topics_view',
                               kwargs={'project_slug': self.project.slug})),
        )
        if self.object is None:
            breadcrumbs += ( ('Add', None),)
        else:
            breadcrumbs += (
                (self.object.as_text(), self.object.get_absolute_url()),
                ('Edit', None)
            )
        return breadcrumbs
