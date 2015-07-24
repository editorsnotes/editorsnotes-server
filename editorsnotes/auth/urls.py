# vim: set tw=0:

from django.conf.urls import patterns, url
from django.contrib.auth import views as auth_views

import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),

    # Django builtins
    url(r'^signin$', auth_views.login, name='signin'),
    url(r'^signout$', auth_views.logout, name='signout'),
    url(r'^account/password_change$', auth_views.password_change, name='password_change', kwargs={
        'post_change_redirect': 'auth:account',
    }),

    url(r'^account/password_reset$', auth_views.password_reset, name='password_reset', kwargs={
        'post_reset_redirect': 'auth:password_reset_done',
    }),
    url(r'^account/password_reset/confirm$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^account/password_reset/done$', auth_views.password_reset_done, name='password_reset_done'),

    # Our own
    url(r'^account/$', views.user_home, name='user_home'),
    url(r'^projects/(?P<project_slug>\w+)$', views.project_home, name='project_home'),

    url(r'^create_account$', views.create_account, name='create_account'),
    url(r'^activate$', views.home, name='account_activate'),
)
