from collections import OrderedDict

from django.shortcuts import get_object_or_404

from rest_framework.response import Response

from editorsnotes.auth.models import Project, LogActivity

from editorsnotes.main.models.base import Administered
from editorsnotes.search import items as items_search

from ..filters import (ElasticSearchFilterBackend,
                       ElasticSearchAutocompleteFilterBackend)
from ..pagination import ESLimitOffsetPagination
from ..serializers import ProjectSerializer


class LinkerMixin(object):
    def __init__(self, *args, **kwargs):
        super(LinkerMixin, self).__init__(*args, **kwargs)
        self._links = []

    def add_link(self, rel, href, method='GET', label=None):
        link = OrderedDict((
            ('rel', rel),
            ('href', href),
            ('method', method)
        ))

        if label:
            link['label'] = label

        self._links.append(link)

    def add_links(self):
        linkers = [linker() for linker in getattr(self, 'linker_classes', [])]
        for linker in linkers:
            links = linker.get_links(self.request, self)
            for link in links:
                self.add_link(**link)

    def get_links(self):
        return self._links

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        self.object = instance
        self.add_links()

        data = OrderedDict([('_links', self.get_links())])
        data.update(serializer.data)

        return Response(data)


class EmbeddedMarkupReferencesMixin(object):
    def get_serializer(self, *args, **kwargs):
        kwargs['include_embeds'] = True
        return super(EmbeddedMarkupReferencesMixin, self)\
            .get_serializer(*args, **kwargs)


class ElasticSearchListMixin(object):
    """
    Mixin that replaces the `list` method with a query to Elasticsearch.
    """
    pagination_class = ESLimitOffsetPagination
    filter_backends = (ElasticSearchFilterBackend,)

    def get_queryset(self):
        model = self.queryset.model
        return items_search.index.make_search_for_model(model)

    def list(self, request, *args, **kwargs):
        """

        Filter backends must expect that the 'queryset' argument will be an
        instance of an elasticsearch-dsl search query, not a django QuerySet
        """
        search_query = self.filter_queryset(self.get_queryset())
        search_results = self.paginate_queryset(search_query)

        prev_link = self.paginator.get_previous_link()
        if prev_link:
            self.add_link('prev', prev_link)

        next_link = self.paginator.get_next_link()
        if next_link:
            self.add_link('next', next_link)

        self.add_links()

        response_data = OrderedDict((
            ('_links', self.get_links()),
        ))

        if hasattr(request, 'project'):
            project_serializer = ProjectSerializer(request.project, context={
                'request': request
            })
            response_data['project'] = project_serializer.data

        response_data['count'] = self.paginator.count
        response_data['results'] = [result['_source']['serialized']
                                    for result in search_results]

        return Response(response_data)

    def ____________list(self, request, *args, **kwargs):
        if 'autocomplete' in request.query_params:
            self.filter_backends += (ElasticSearchAutocompleteFilterBackend,)
            result = self.filter_queryset(None)
            data = {
                'count': result['hits']['total'],
                'results': []
            }
            for doc in result['hits']['hits']:
                r = OrderedDict()
                r['type'] = doc['_type']
                r['title'] = (
                    doc['highlight']['display_title'][0]
                    if 'highlight' in doc else
                    doc['fields']['display_title'])
                r['url'] = doc['fields']['serialized.url']
                data['results'].append(r)


class ProjectSpecificMixin(object):
    """
    Mixin for API views that populates project information in various places

        1. Request object, based on presence of `project_slug` in request
        kwargs.
        2. Serializer context, under the `project` key.
        3. As a queryset filter, if the model being filtered has a `project`
        field.
    """
    def initial(self, request, *args, **kwargs):
        project_slug = kwargs.pop('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        request._request.project = project

        request = super(ProjectSpecificMixin, self)\
            .initial(request, *args, **kwargs)

        return request

    def perform_create(self, serializer):
        serializer.save(project=self.request.project,
                        creator=self.request.user,
                        last_updater=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_updater=self.request.user)

    def get_queryset(self):
        qs = super(ProjectSpecificMixin, self).get_queryset()
        if hasattr(qs.model, 'project'):
            qs = qs.filter(project_id=self.request.project.id)
        return qs


class LogActivityMixin(object):
    def _should_log_activity(self, obj):
        return isinstance(obj, Administered)

    def make_log_activity(self, obj, action, commit=True):
        log_obj = LogActivity(
            user=self.request.user,
            project=self.request.project,
            content_object=obj,
            display_title=obj.as_text(),
            action=action)
        if commit:
            log_obj.save()
        self.log_obj = log_obj
        return log_obj
