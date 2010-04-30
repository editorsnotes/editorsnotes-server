from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     { 'document_root': '/Users/ryanshaw/Code/editorsnotes/editorsnotes/static' }),
)
urlpatterns += patterns('editorsnotes.main.views',
    url(r'^$', 'index', name='index_view'),
    url(r'^t/(?P<slug>[-a-z0-9]+)/$', 'term', name='term_view'),
)
