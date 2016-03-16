# vim: set tw=0:

from django.conf.urls import patterns, url, include
from django.conf import settings
from django.views.generic.base import RedirectView

urlpatterns = [
    # API
    url(r'^', include('editorsnotes.api.urls', namespace='api', app_name='api')),

    # Auth
    url(r'^auth/', include('editorsnotes.auth.urls', namespace='auth', app_name='auth')),
]
