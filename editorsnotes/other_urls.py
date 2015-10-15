# vim: set tw=0:

from django.conf.urls import patterns, url, include
from django.conf import settings
from django.views.generic.base import RedirectView
from editorsnotes.main.views.auth import CustomBrowserIDVerify

# These will be intercepted by apache in production
urlpatterns = patterns('',
    (r'^favicon.ico$', RedirectView.as_view(url='/static/style/icons/favicon.ico')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT }),
    (r'^proxy$', 'editorsnotes.main.views.proxy'),
)

# Auth patterns
urlpatterns += patterns('',
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', { 'redirect_field_name': 'return_to' }, name='user_login_view'),
    url(r'^accounts/logout/$', 'editorsnotes.main.views.auth.user_logout', name='user_logout_view'),
    url(r'^accounts/profile/$', 'editorsnotes.main.views.auth.user'),
    url(r'^accounts/profile/feedback/$', 'editorsnotes.main.views.auth.user_feedback', name='user_feedback_view'),
    url(r'^accounts/browserid/$', CustomBrowserIDVerify.as_view(), name='browserid_verify'),
    url(r'^users/(?P<username>[\w@\+\.\-]+)/$', 'editorsnotes.main.views.auth.user', name='user_view'),
)

# Base patterns
urlpatterns += patterns('editorsnotes.main.views.navigation',
    url(r'^$', 'index', name='index_view'),
    url(r'^about/$', 'about', name='about_view'),
    url(r'^about/test/$', 'about_test'),
    url(r'^search/$', 'search', name='search_view'),
)

# Admin patterns
urlpatterns += patterns('',
    url(r'^projects/(?P<project_slug>\w+)/', include('editorsnotes.admin.urls', namespace='admin', app_name='admin')),
    url(r'^projects/add/', 'editorsnotes.admin.views.projects.add_project', name='add_project_view'),
)

# Main model patterns
urlpatterns += patterns('',
    url(r'^', include('editorsnotes.main.urls')),
)
