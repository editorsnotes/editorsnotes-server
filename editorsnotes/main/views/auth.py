import re

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django_browserid.views import Verify
import reversion

from editorsnotes.auth.models import (
    User, Project, ProjectInvitation, UserFeedback)
from editorsnotes.search import get_index
from ..forms import UserFeedbackForm

@reversion.create_revision()
def create_invited_user(email):
    invitation = ProjectInvitation.objects.filter(email=email)
    if not invitation.exists():
        return None
    invitation = invitation.get()

    project = invitation.project
    role = invitation.project_role

    username = re.sub(r'[^\w\-.]', '', email[:email.rindex('@')])[:29]
    if User.objects.filter(username=username).exists():
        existing_names = [
            u.username[len(username):] for u in
            User.objects.filter(username__startswith=username)]
        username += str([
            i for i in range(0, 10) if str(i) not in existing_names][0])

    new_user = User(username=username, email=email)
    new_user.set_unusable_password()
    new_user.save()

    role.users.add(new_user)
    invitation.delete()

    return new_user

class CustomBrowserIDVerify(Verify):
    failure_url = '/accounts/login/'
    def get_success_url(self):
        return self.request.GET.get('return_to',
                                    self.request.user.get_absolute_url())

def user_logout(request):
    auth.logout(request)
    return render_to_response(
        'logout.html', context_instance=RequestContext(request))

def user(request, username=None):
    o = {}
    if not username:
        user = request.user
        if not user or not user.is_authenticated():
            return HttpResponseRedirect(reverse('user_login_view'))
        o['own_profile'] = True
    else:
        user = get_object_or_404(User, username=username)
        o['own_profile'] = user == request.user
    o['user'] = user


    activity_index = get_index('activity')
    o['activities'] = activity_index.get_activity_for(user)

    # FIX
    # o['profile'] = get_for(user)
    # o['affiliation'] = o['profile'].affiliation
    # o['project_role'] = (o['profile'].get_project_role(o['affiliation'])
    #                      if o['affiliation'] else None)

    if ['own_profile']:
        o['zotero_status'] = user.zotero_key and user.zotero_uid
    return render_to_response(
        'user.html', o, context_instance=RequestContext(request))

@login_required
def user_feedback(request):
    o = {}
    template = 'user_feedback.html'
    initial = { 'user': request.user }
    if request.method == 'POST':
        o['form'] = UserFeedbackForm(request.POST)
        if o['form'].is_valid():
            obj = o['form'].save(commit=False)
            obj.user = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, 'Feedback submitted.')
            return HttpResponseRedirect(request.path)
    else:
        o['form'] = UserFeedbackForm()
    return render_to_response(
        template, o, context_instance=RequestContext(request))

@login_required
def all_feedback(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    feedback = UserFeedback.objects.select_related('user').order_by('-created')
    return render_to_response(
        'all_feedback.html', {'feedback': feedback},
        context_instance=RequestContext(request))


def project(request, project_slug):
    o = {}
    o['project'] = get_object_or_404(Project, slug=project_slug)
    activity_index = get_index('activity')
    o['activities'] = activity_index.get_activity_for(o['project'])

    if request.user.is_authenticated():
        o['project_role'] = o['project'].get_role_for(request.user)

        o['can_view_roster'] = request.user.has_project_perm(
            o['project'], 'main.view_project_roster')
        o['can_change_roster'] = request.user.has_project_perm(
            o['project'], 'main.change_project_roster')
        o['can_change_featured_items'] = request.user.has_project_perm(
            o['project'], 'main.change_featureditem')
        o['can_change_project'] = request.user.has_project_perm(
            o['project'], 'main.change_project')

        o['show_edit_row'] = any((
            o['can_view_roster'], o['can_change_roster'],
            o['can_change_featured_items'], o['can_change_project']))
    return render_to_response(
        'project.html', o, context_instance=RequestContext(request))

def all_projects(request):
    return HttpResponse('hi')
