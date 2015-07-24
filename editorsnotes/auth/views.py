from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext


def home(request):
    "Redirect either to currently logged in user or sign in page."
    if request.user and request.user.is_authenticated():
        return redirect('auth:user_home')
    else:
        return redirect('auth:signin')


def create_account(request):
    "Make a request to create an account."
    return render_to_response(
        'sign_up.html', context_instance=RequestContext(request))


def activate(request):
    "Activate a request to create an account"
    return render_to_response(
        'activate.html', context_instance=RequestContext(request))


@login_required
def user_home(request):
    "View/change name, email, and other details for current user."
    return render_to_response(
        'user_home.html', context_instance=RequestContext(request))


@login_required
def project_home(request, project_slug):
    "View/change project name, slug, and roster."
    return render_to_response(
        'project_home.html', context_instance=RequestContext(request))
