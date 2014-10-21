from collections import Counter, OrderedDict

from django.conf import settings
from django.db.models.deletion import Collector
from django.utils.text import force_text

from rest_framework.decorators import api_view
from rest_framework.generics import (
    GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.utils import formatting
import reversion

from editorsnotes.main.models import Project
from editorsnotes.main.models.auth import (RevisionProject, LogActivity,
                                           RevisionLogActivity,
                                           ADDITION, CHANGE, DELETION)
from editorsnotes.main.models.base import Administered
from editorsnotes.search import get_index

from ..filters import (ElasticSearchFilterBackend,
                       ElasticSearchAutocompleteFilterBackend)
from ..permissions import ProjectSpecificPermissions


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
            return super(ElasticSearchRetrieveMixin, self).retrieve(request, *args, **kwargs)

        # Still need to get the object to check for perms
        self.object = self.get_object()
        en_index = get_index('main')
        data = en_index.data_for_object(self.object)
        return Response(data['_source']['serialized'])

class ElasticSearchListMixin(ListModelMixin):
    """
    Mixin that replaces the `list` method with a query to Elasticsearch.
    """
    def list(self, request, *args, **kwargs):

        if not settings.ELASTICSEARCH_ENABLED:
            return super(ElasticSearchListMixin, self).list(request, *args, **kwargs)

        if 'autocomplete' in request.QUERY_PARAMS:
            self.filter_backend = ElasticSearchAutocompleteFilterBackend
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
        else:
            self.filter_backend = ElasticSearchFilterBackend
            result = self.filter_queryset(None)
            data = {
                'count': result['hits']['total'],
                'next': None,
                'previous': None,
                'results': [ doc['_source']['serialized'] for doc in
                             result['hits']['hits'] ]
            }
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
    def initialize_request(self, request, *args, **kwargs):
        request = super(ProjectSpecificMixin, self)\
                .initialize_request(request, *args, **kwargs)
        request._request.project = Project.objects.get(
            slug=kwargs.pop('project_slug'))
        return request
    def get_serializer_context(self):
        context = super(ProjectSpecificMixin, self).get_serializer_context()
        context['project'] = self.request.project
        return context
    def get_queryset(self):
        qs = super(ProjectSpecificMixin, self).get_queryset()
        if hasattr(qs.model, 'project'):
            qs = qs.filter(project_id=self.request.project.id)
        return qs

rel_model = {
    'notesection': lambda original, related: related.note,
    'topicassignment': lambda original, related: related.topic \
        if related.topic != original else related.content_object,
    'citation': lambda original, related: related.content_object,
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
            instances = filter(lambda instance: hasattr(instance, 'get_absolute_url'), instances)
            counter = Counter(instances)
            ret['items'] += [{
                'name': force_text(instance),
                'preview_url': request._request.build_absolute_uri(instance.get_absolute_url()),
                'type': model._meta.verbose_name,
                'count': count
            } for instance, count in counter.items()]

        ret['items'].sort(key=lambda item: item['type'] != obj._meta.verbose_name)

        return Response(ret)

    def get_view_description(self, html=False):
        description = self.__doc__ or """
        Returns a nested list of objects that would be also be deleted when this
        object is deleted.
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
class BaseListAPIView(ProjectSpecificMixin, LogActivityMixin, ListCreateAPIView):
    paginate_by = 50
    paginate_by_param = 'page_size'
    permission_classes = (ProjectSpecificPermissions,)
    parser_classes = (JSONParser,)
    def pre_save(self, obj):
        obj.creator = self.request.user
        if hasattr(obj.__class__, 'last_updater'):
            obj.last_updater = self.request.user
        super(BaseListAPIView, self).pre_save(obj)
    def post_save(self, obj, created):
        if self._should_log_activity(obj):
            self.make_log_activity(obj, ADDITION)

@create_revision_on_methods('update', 'destroy')
class BaseDetailView(ProjectSpecificMixin, LogActivityMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (ProjectSpecificPermissions,)
    parser_classes = (JSONParser,)
    def post_save(self, obj, created):
        if self._should_log_activity(obj):
            self.make_log_activity(obj, CHANGE)
    def pre_delete(self, obj):
        self._deleted_id = obj.id
    def post_delete(self, obj):
        if self._should_log_activity(obj):
            log_obj = self.make_log_activity(obj, DELETION, commit=False)
            log_obj.object_id = self._deleted_id
            log_obj.save()
    def pre_save(self, obj):
        if hasattr(obj.__class__, 'last_updater'):
            obj.last_updater = self.request.user
        super(BaseDetailView, self).pre_save(obj)

@api_view(('GET',))
def root(request):
    return Response({
        'auth-token': reverse('api:obtain-auth-token', request=request),
        'topics': reverse('api:api-topic-nodes-list', request=request),
        'projects': reverse('api:api-projects-list', request=request),
        'search': reverse('api:api-search', request=request)
        #'notes': reverse('api:api-notes-list'),
        #'documents': reverse('api:api-documents-list')
    })
