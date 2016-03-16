# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponseForbidden, HttpResponseRedirect, HttpResponseBadRequest)
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from reversion import revisions as reversion

from editorsnotes.auth.models import Project

from .. import forms
from common import VIEW_ERROR_MSG, CHANGE_ERROR_MSG

@login_required
@reversion.create_revision()
def project_roster(request, project_slug):
    o = {}
    user = request.user


    project_qs = Project.objects\
            .prefetch_related('roles__group__permissions')\
            .select_related('roles__group__permissions',
                            'roles__group__users')
    project = get_object_or_404(project_qs, slug=project_slug)

    o['breadcrumb'] = (
        (project.name, project.get_absolute_url()),
        ('Roster', None)
    )

    can_view = user.has_project_perm(project, 'main.view_project_roster')
    if not can_view:
        return HttpResponseForbidden(VIEW_ERROR_MSG.format(project))
    can_change = user.has_project_perm(project, 'main.change_project_roster')

    ProjectRosterFormSet = forms.make_project_roster_formset(project)
    ProjectInvitationFormSet = forms.make_project_invitation_formset(project)

    if request.method == 'POST':

        if not can_change:
            return HttpResponseForbidden(CHANGE_ERROR_MSG.format(project))

        if request.POST.get('roster-TOTAL_FORMS'):
            o['roster_formset'] = ProjectRosterFormSet(request.POST, prefix='roster')
            if o['roster_formset'].is_valid():
                o['roster_formset'].save()
                messages.add_message(request, messages.SUCCESS,
                                     'Roster for {} saved.'.format(project.name))
                return HttpResponseRedirect(request.path)
            else:
                o['invitation_formset'] = ProjectInvitationFormSet(prefix='invitation')

        elif request.POST.get('invitation-TOTAL_FORMS'):
            o['invitation_formset'] = ProjectInvitationFormSet(request.POST,
                                                               prefix='invitation')
            if o['invitation_formset'].is_valid():
                for form in o['invitation_formset']:
                    if form.cleaned_data.get('DELETE', False):
                        if form.instance:
                            form.instance.delete()
                        continue
                    obj = form.save(commit=False)
                    if not obj.id:
                        if not form.cleaned_data.has_key('email'):
                            continue
                        obj.creator = request.user
                        obj.project = project
                    obj.save()
                messages.add_message(request, messages.SUCCESS,
                                     'Roster for {} saved.'.format(project.name))
                return HttpResponseRedirect(request.path)
            else:
                o['roster_formset'] = ProjectRosterFormSet(prefix='roster')
        else:
            return HttpResponseBadRequest()


    elif can_change:
        o['roster_formset'] = ProjectRosterFormSet(prefix='roster')
        o['invitation_formset'] = ProjectInvitationFormSet(prefix='invitation')

    o['project'] = project
    o['roster'] = [(u, project.get_role_for(u))
                   for u in project.members.order_by('-last_login')]

    return render_to_response(
        'project_roster.html', o, context_instance=RequestContext(request))

@login_required
def change_project_roles(request, project_slug):
    o = {}

    o['project'] = project = get_object_or_404(Project, slug=project_slug)

    o['breadcrumb'] = (
        (project.name, project.get_absolute_url()),
        ('Roster', reverse('admin:main_project_roster_change',
                           kwargs={'project_slug': project.slug})),
        ('Roles', None),
    )

    can_view = request.user.has_project_perm(project, 'main.change_project_roster')
    if not can_view:
        return HttpResponseForbidden(VIEW_ERROR_MSG.format(project))

    role_formset = forms.make_project_permissions_formset(project)

    if request.method == 'POST':
        formset = role_formset(request.POST)
        if formset.is_valid():
            formset.save()
            messages.add_message(
                request, messages.SUCCESS,
                'Saved roles for {}'.format(project))
            return HttpResponseRedirect(request.path)
        else:
            o['formset'] = formset
    else:
        o['formset'] = role_formset()

    return render_to_response(
        'project_roles.html', o, context_instance=RequestContext(request))
