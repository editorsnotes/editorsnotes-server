from collections import Counter

from django.db.models.deletion import Collector
from django.utils.text import force_text

from rest_framework.generics import (
    GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.utils import formatting, model_meta
from reversion import revisions as reversion

from editorsnotes.auth.models import (RevisionProject, RevisionLogActivity,
                                      ADDITION, CHANGE, DELETION)

from ..permissions import ProjectSpecificPermissions
from .mixins import LogActivityMixin, ProjectSpecificMixin


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

        for model, instances in list(collector.data.items()):
            display_obj = rel_model.get(model._meta.model_name,
                                        lambda original, related: related)
            instances = [display_obj(obj, instance) for instance in instances]
            instances = [instance for instance in instances if hasattr(instance, 'get_absolute_url')]
            counter = Counter(instances)
            ret['items'] += [{
                'name': force_text(instance),
                'preview_url': request._request.build_absolute_uri(
                    instance.get_absolute_url()),
                'type': model._meta.verbose_name,
                'count': count
            } for instance, count in list(counter.items())]

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
                     RetrieveUpdateDestroyAPIView):
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
