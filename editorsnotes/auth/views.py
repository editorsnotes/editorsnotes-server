from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.http import urlsafe_base64_decode

from .forms import ENUserCreationForm, UserProfileForm, ProjectForm
from .models import User
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
    else:
        form = UserProfileForm(instance=request.user)
    return render_to_response(
        'user_home.html',
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

            form = ProjectForm()
    else:
        form = ProjectForm()
    return render_to_response(
        'user_project_settings.html',
        {
            'page': 'projects',
            'form': form
        },
        RequestContext(request))


@login_required
def project_home(request, project_slug):
    "View/change project name, slug, and roster."
    return render_to_response(
        'project_home.html', context_instance=RequestContext(request))
