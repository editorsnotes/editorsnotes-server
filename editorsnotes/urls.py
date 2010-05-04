from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.forms import AuthenticationForm

admin.autodiscover()

# TODO: get rid of this by using settings.yml to assign title to id_username, id_password
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'title'
        self.fields['password'].widget.attrs['class'] = 'title'

urlpatterns = patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login',
     { 'authentication_form': CustomAuthenticationForm }),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^search/', include('haystack.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     { 'document_root': '/Users/ryanshaw/Code/editorsnotes/editorsnotes/static' }),
)

urlpatterns += patterns('editorsnotes.main.views',
    url(r'^$', 'index', name='index_view'),
    url(r'^t/(?P<term_slug>[-a-z0-9]+)/$', 'term', name='term_view'),
    url(r'^n/(?P<note_id>\d+)/$', 'note', name='note_view'),
)
