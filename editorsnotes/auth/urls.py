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
    url(r'^account/password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^account/password_reset/done$', auth_views.password_reset_done, name='password_reset_done'),

    # Our own
    url(r'^account/$', views.user_home, name='user_home'),
    url(r'^account/settings/$', views.user_account_settings, name='user_account_settings'),
    url(r'^account/projects/$', views.user_project_settings, name='user_project_settings'),

    # Projects
    url(r'^projects/(?P<project_slug>\w+)$', views.project_home, name='project_home'),

    # Account creation things
    url(r'^account/create$', views.create_account, name='create_account'),
    url(r'^account/activate/sent$', views.activation_sent, name='activation_sent'),
    url(r'^account/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate_account, name='activate_account'), 

)
