from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.http import urlsafe_base64_decode

from .forms import ENUserCreationForm, UserProfileForm, ProjectForm
from .models import User, Project
from .utils import send_activation_email


def home(request):
    "Redirect either to currently logged in user or sign in page."
    if request.user and request.user.is_authenticated():
        if request.user.is_active:
            return redirect('auth:user_home')
        else:
            return redirect('auth:activation_sent')
    else:
        return redirect('auth:signin')


def create_account(request):
    "Make a request to create an account."
    if request.method == 'POST':
        form = ENUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = user.confirmed = False
            user.save()

            send_activation_email(request, user)
            return redirect('auth:activation_sent')

    else:
        form = ENUserCreationForm()
    return render_to_response(
        'create_account.html',
        { 'form': form },
        RequestContext(request))


def activation_sent(request):
    return render_to_response(
        'activation_sent.html', context_instance=RequestContext(request))


def activate_account(request, uidb64=None, token=None):
    "Activate a request to create an account"
    assert uidb64 is not None and token is not None

    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        if user.is_active:
            raise Http404()
        user.is_active = True
        user.confirmed = True
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        user.save()
        login(request, user)
        return redirect('auth:user_home')

    raise Http404()


@login_required
def user_home(request):
    "View/change name and other details for current user."
    successful_change = False

    if request.method == 'POST':
        form = UserProfileForm(data=request.POST, instance=request.user)
        if form.is_valid():
            successful_change = True
            form.save()

    form = UserProfileForm(instance=request.user)

    return render_to_response(
        'user_profile_settings.html',
        {
            'page': 'profile',
            'form': form,
            'successful_change': successful_change
        },
        RequestContext(request))


@login_required
def user_account_settings(request):
    "View/change username, password, email"
    return render_to_response(
        'user_account_settings.html',
        { 'page': 'account' },
        RequestContext(request))


@login_required
def user_project_settings(request):
    "Add new project for user"
    if request.method == 'POST':
        form = ProjectForm(data=request.POST)
        if form.is_valid():
            project = form.save()

            # Add the user to the editor role
            project.roles.get().group.user_set.add(request.user)
            return redirect('auth:user_project_settings')
    else:
        form = ProjectForm()
    return render_to_response(
        'user_project_settings.html',
        {
            'page': 'create_project',
            'form': form
        },
        RequestContext(request))


@login_required
def project_settings(request, project_slug):
    "View/change project name, slug, and roster."
    project = get_object_or_404(Project, slug=project_slug)
    return render_to_response(
        'project_settings.html',
        {
            'project_page': project.slug,
            'project': project
        },
        RequestContext(request))


# FIXME: The following is code from an old view. We should reuse the about_test
# code for requiring a minimal honeytrap
#
# import os
# from random import randint
# 
# from django.conf import settings
# from django.contrib import messages
# from django.core.mail import mail_admins
# from django.http import (
#     HttpResponse, HttpResponseForbidden, HttpResponseRedirect)
# from django.shortcuts import render_to_response
# from django.template import RequestContext
# 
# from PIL import Image, ImageDraw, ImageFont
# 
# from ..forms import FeedbackForm
# 
# 
# def about_test(request):
#     x, y = (100, 38)
#     img = Image.new('RGBA', (x, y), (255, 255, 255))
#     draw = ImageDraw.Draw(img)
#     font = ImageFont.truetype(
#         os.path.join(settings.STATIC_ROOT, 'style', 'DejaVuSans-Bold.ttf'), 24)
#     i, s, j = (randint(10, 20), ('+', '-')[randint(0, 1)], randint(1, 9))
#     text = '%s %s %s' % (i, s, j)
# 
#     result = i + j if s == '+' else i - j
# 
#     draw.text((9, 5), text, (50, 50, 50), font=font)
# 
#     for i in xrange(0, 500):
#         draw.point((randint(0, x), randint(0, y)),
#                    [(xx, xx, xx) for xx in (randint(100, 180),)][0])
# 
#     request.session['test_answer'] = result
# 
#     response = HttpResponse(content_type="image/png")
#     img.save(response, 'PNG')
# 
#     return response
# 
# 
# def about(request):
#     o = {}
# 
#     if request.method == 'POST':
# 
#         bad_answers = request.session.setdefault('bad_answers', 0)
#         if bad_answers > 3:
#             return HttpResponseForbidden(
#                 'Too many failed attempts. Try again later.')
# 
#         o['form'] = FeedbackForm(request.POST)
#         if o['form'].is_valid():
# 
#             test_answer = request.POST.get('testanswer', '')
#             is_good_answer = (
#                 test_answer.isdigit() and
#                 int(test_answer) == request.session['test_answer']
#             )
#             if is_good_answer:
#                 request.session.pop('bad_answers')
# 
#                 choice = o['form'].cleaned_data['purpose']
#                 subj = '(%s) %s' % (
#                     dict(o['form'].fields['purpose'].choices)[choice],
#                     o['form'].cleaned_data['name'])
#                 msg = 'reply to: {email}\n\n{message}'.format(
#                     **o['form'].cleaned_data)
#                 mail_admins(subj, msg, fail_silently=True)
#                 messages.add_message(
#                     request, messages.SUCCESS,
#                     'Thank you. Your feedback has been submitted.')
#                 return HttpResponseRedirect('/about/')
#             else:
#                 request.session['bad_answers'] = bad_answers + 1
#                 o['bad_answer'] = True
#                 return render_to_response(
#                     'about.html', o, context_instance=RequestContext(request))
#     else:
#         o['form'] = FeedbackForm()
#     return render_to_response(
#         'about.html', o, context_instance=RequestContext(request))
