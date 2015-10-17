from collections import Counter, OrderedDict

from django.conf import settings
from django.db.models.deletion import Collector
from django.shortcuts import get_object_or_404
from django.utils.text import force_text

from elasticsearch_dsl import Search
from rest_framework.decorators import api_view
from rest_framework.generics import (
    GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.utils import formatting, model_meta
import reversion

from editorsnotes.auth.models import (
    Project, RevisionProject, LogActivity, RevisionLogActivity,
    ADDITION, CHANGE, DELETION)

from editorsnotes.main.models import Note, Topic, Document
from editorsnotes.main.models.base import Administered
from editorsnotes.search import items as items_search

from ..filters import (ElasticSearchFilterBackend,
                       ElasticSearchAutocompleteFilterBackend)
from ..pagination import ESLimitOffsetPagination
from ..permissions import ProjectSpecificPermissions
from ..serializers import ProjectSerializer


def create_revision_on_methods(*methods):
    """
    Class decorator to specify that revisions should be made on class methods.

    Project metadata will be attached based on the request object, and the
    reversion model will be attached to a log obj attached to the view if it
    exists.
    """
    def make_revision_wrapper(fn):
        def wrapped(self, request, *args, **kwargs):
            with reversion.create_revision():
                ret = fn(self, request, *args, **kwargs)
                reversion.set_user(request.user)
                reversion.add_meta(RevisionProject, project=request.project)
                if getattr(self, 'log_obj', None):
                    reversion.add_meta(RevisionLogActivity,
                                       log_activity=self.log_obj)
            return ret
        return wrapped

    def klass_wrapper(klass):
        for method_name in methods:
            old_method = getattr(klass, method_name)
            wrapped = make_revision_wrapper(old_method)
            setattr(klass, method_name, wrapped)
        return klass
    return klass_wrapper


class ElasticSearchRetrieveMixin(RetrieveModelMixin):
    """
    Mixin that replaces the `retrieve` method with a query to Elasticsearch.
    """
    def retrieve(self, request, *args, **kwargs):

        if not settings.ELASTICSEARCH_ENABLED:
            return super(ElasticSearchRetrieveMixin, self)\
                .retrieve(request, *args, **kwargs)

        # Still need to get the object to check for perms
        self.object = self.get_object()

        data = items_search.data_for_object(self.object)
        return Response(data['_source']['serialized'])


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

rel_model = {
    'notesection': lambda original, related: related.note,
    'topicassignment': lambda original, related: (
        related.topic if related.topic != original else related.content_object
    ),
    'scan': lambda original, related: related.document
}


class DeleteConfirmAPIView(ProjectSpecificMixin, GenericAPIView):
    permission_classes = (ProjectSpecificPermissions,)

    def get(self, request, **kwargs):
        obj = self.get_object()
        collector = Collector(using='default')
        collector.collect([obj])
        collector.sort()

        ret = {'items': []}

        for model, instances in collector.data.items():
            display_obj = rel_model.get(model._meta.model_name,
                                        lambda original, related: related)
            instances = [display_obj(obj, instance) for instance in instances]
            instances = filter(
                lambda instance: hasattr(instance, 'get_absolute_url'),
                instances)
            counter = Counter(instances)
            ret['items'] += [{
                'name': force_text(instance),
                'preview_url': request._request.build_absolute_uri(
                    instance.get_absolute_url()),
                'type': model._meta.verbose_name,
                'count': count
            } for instance, count in counter.items()]

        ret['items'].sort(
            key=lambda item: item['type'] != obj._meta.verbose_name)

        return Response(ret)

    def get_view_description(self, html=False):
        description = self.__doc__ or """
        Returns a nested list of objects that would be also be deleted when
        this object is deleted.
        """
        description = formatting.dedent(description)
        if html:
            return formatting.markup_description(description)
        return description


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


@create_revision_on_methods('create')
class BaseListAPIView(ProjectSpecificMixin, LogActivityMixin,
                      ListCreateAPIView):
    paginate_by = 50
    paginate_by_param = 'page_size'
    permission_classes = (ProjectSpecificPermissions,)
    parser_classes = (JSONParser,)

    def perform_create(self, serializer):
        ModelClass = serializer.Meta.model
        field_info = model_meta.get_field_info(ModelClass)
        kwargs = {}
        kwargs['creator'] = self.request.user
        if 'last_updater' in field_info.relations:
            kwargs['last_updater'] = self.request.user
        if 'project' in field_info.relations:
            kwargs['project'] = self.request.project
        instance = serializer.save(**kwargs)
        if self._should_log_activity(instance):
            self.make_log_activity(instance, ADDITION)


@create_revision_on_methods('update', 'destroy')
class BaseDetailView(ProjectSpecificMixin, LogActivityMixin,
                     LinkerMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (ProjectSpecificPermissions,)
    parser_classes = (JSONParser,)

    def perform_update(self, serializer):
        ModelClass = serializer.Meta.model
        field_info = model_meta.get_field_info(ModelClass)
        kwargs = {}
        if 'last_updater' in field_info.relations:
            kwargs['last_updater'] = self.request.user
        instance = serializer.save(**kwargs)
        if self._should_log_activity(instance):
            self.make_log_activity(instance, CHANGE)

    def perform_destroy(self, instance):
        deleted_id = instance.id
        instance.delete()
        if self._should_log_activity(instance):
            log_obj = self.make_log_activity(instance, DELETION, commit=False)
            log_obj.object_id = deleted_id
            log_obj.save()


@api_view(('GET',))
def root(request, format=None):
    return Response({
        'auth-token': reverse('api:obtain-auth-token', request=request),
        'projects': reverse('api:projects-list', request=request),
        'search': reverse('api:search', request=request)
        # 'notes': reverse('api:notes-list'),
        # 'documents': reverse('api:documents-list')
    })


def search_model(Model, query):
    query = query.to_dict()
    query['fields'] = ['display_title', 'display_url']
    results = items_search.search_model(Model, query)
    return [
        {
            'title': result['fields']['display_title'][0],
            'url': result['fields']['display_url'][0]
        }
        for result in results['hits']['hits']
    ]


@api_view(['GET'])
def browse(request, format=None):
    es_query = Search().sort('-serialized.last_updated')[:10]
    ret = OrderedDict()

    ret['topics'] = search_model(Topic, es_query)
    ret['documents'] = search_model(Document, es_query)
    ret['notes'] = search_model(Note, es_query.filter(
        'term', **{'serialized.is_private': 'false'}
    ))

    return Response(ret)
