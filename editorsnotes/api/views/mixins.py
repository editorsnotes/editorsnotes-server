from collections import OrderedDict

from django.shortcuts import get_object_or_404

from rest_framework.response import Response

from editorsnotes.api.serializers import ProjectSerializer
from editorsnotes.auth.models import Project, LogActivity
from editorsnotes.main.models.base import Administered
from editorsnotes.search import items_index

from ..serializers.hydra import hydra_class_for_type
from ..pagination import ESLimitOffsetPagination


class EmbeddedHydraClassMixin(object):
    # Putting this in finalize_response instead of get_serializer because we
    # don't call that method when using Elasticsearch.
    def finalize_response(self, request, response, *args, **kwargs):
        response = super(EmbeddedHydraClassMixin, self)\
            .finalize_response(request, response, *args, **kwargs)

        project = self.request.project

        # Don't add anything if there's no content (i.e. in a successful
        # DELETE operation)
        if not response.data:
            return response

        hydra_class = hydra_class_for_type(
            self.queryset.model.__name__, project, request)

        new_data = OrderedDict()

        for key, val in response.data.items():
            new_data[key] = val
            if key == 'type':
                new_data['hydra_type'] = hydra_class['@id']

        if 'embedded' not in response.data:
            new_data['embedded'] = OrderedDict()

        new_data['embedded'][hydra_class['@id']] = hydra_class
        response.data = new_data

        return response


class EmbeddedMarkupReferencesMixin(object):
    def get_serializer(self, *args, **kwargs):
        kwargs['include_embeds'] = True
        return super(EmbeddedMarkupReferencesMixin, self)\
            .get_serializer(*args, **kwargs)


class ElasticSearchListMixin(object):
    """
    Mixin that replaces the `list` method with a query to Elasticsearch.
    """

    es_filter_backends = []
    pagination_class = ESLimitOffsetPagination

    def filter_search(self, search):
        for backend in list(self.es_filter_backends):
            search = backend().filter_search(self.request, search, self)
        return search

    def paginate_search(self, search):
        "Proxy method to paginate_queryset to make things less confusing."
        return self.paginator.paginate_search(search, self.request, view=self)

    def get_es_search(self):
        "By default, return a search for the queryset model"
        return items_index\
            .make_search_for_model(self.queryset.model)\
            .sort('-serialized.last_updated')

    def process_es_result(self, result):
        return result['_source']['serialized']

    def list(self, request, *args, **kwargs):
        search = getattr(self, 'search', self.get_es_search())
        search = self.filter_search(search)

        # Responses will __always__ be paginated. `paginate_search` will
        # execute the query and return the hits as indexed in Elasticsearch.
        results = self.paginate_search(search)

        prev_link = self.paginator.get_previous_link()
        next_link = self.paginator.get_next_link()

        data = OrderedDict((
            ('count', self.paginator.count),
            ('prev', prev_link),
            ('next', next_link),
            ('results', map(self.process_es_result, results))
        ))

        if hasattr(request, 'project'):
            serializer = ProjectSerializer(instance=request.project,
                                           context={'request': request})
            project_url = serializer.data['url']
            data['project'] = project_url
            data['embedded'] = {project_url: serializer.data}

        return Response(data)


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
