# vim: set tw=0:

from django.conf.urls import patterns, url
from django.contrib.auth import views as auth_views

import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),

    # Django builtins
    url(r'^signin$', auth_views.login, name='signin', kwargs={
        'template_name': 'sign_in.html'
    }),

    url(r'^signout$', auth_views.logout, name='signout', kwargs={
        'template_name': ''
    }),

    url(r'^account/password_change$', auth_views.password_change, name='password_change', kwargs={
        'post_change_redirect': 'auth:account',
        'template_name': ''
    }),

    url(r'^account/password_reset$', auth_views.password_reset, name='password_reset', kwargs={
        'post_reset_redirect': 'auth:password_reset_done',
        'template_name': ''
    }),

    url(r'^account/password_reset/done$', auth_views.password_reset_done, name='password_reset_done', kwargs={
        'template_name': ''
    }),

    url(r'^account/password_reset/confirm$', auth_views.password_reset_confirm, name='password_reset_confirm', kwargs={
        'template_name': ''
    }),

    # Our own
    url(r'^account/$', views.user_home, name='user_home'),
    url(r'^p/(?P<project_slug>\w+)$', views.project_home, name='project_home'),

    url(r'^create_account$', views.create_account, name='create_account'),
    url(r'^activate$', views.home, name='user_home'),
)
