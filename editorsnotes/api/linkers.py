from django.contrib.auth import get_permission_codename
from rest_framework.reverse import reverse

class AddProjectObjectLinker(object):
    def get_links(self, request, view):
        model = view.queryset.model
        project = request.project
        user = request.user

        perm = '{}.{}'.format(model._meta.app_label,
                              get_permission_codename('add', model._meta))

        if user.is_authenticated() and user.has_project_perm(project, perm):
            view_name = 'api:{}-list'.format(model._meta.verbose_name_plural.lower())
            href = reverse(view_name, args=[request.project.slug], request=request)
            return [{
                'rel': 'add',
                'href': href,
                'method': 'POST',
            }]
        else:
            return []

class EditProjectObjectLinker(object):
    def get_links(self, request, view):
        model = view.queryset.model
        project = request.project
        user = request.user

        perm = '{}.{}'.format(model._meta.app_label,
                              get_permission_codename('change', model._meta))

        if user.is_authenticated() and user.has_project_perm(project, perm):
            href = request.build_absolute_uri(view.object.get_absolute_url())
            return [{
                'rel': 'edit',
                'href': href,
                'method': 'PUT',
            }]
        else:
            return []

class DeleteProjectObjectLinker(object):
    def get_links(self, request, view):
        model = view.queryset.model
        project = request.project
        user = request.user

        perm = '{}.{}'.format(model._meta.app_label,
                              get_permission_codename('delete', model._meta))

        if user.is_authenticated() and user.has_project_perm(project, perm):
            href = request.build_absolute_uri(view.object.get_absolute_url())
            return [{
                'rel': 'delete',
                'href': href,
                'method': 'DELETE',
            }]
        else:
            return []
