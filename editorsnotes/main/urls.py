# vim: set tw=0:

from django.conf.urls import patterns, url

urlpatterns = patterns('editorsnotes.main.views.auth',
    url(r'^feedback/$', 'all_feedback', name='all_feedback_view'),
    url(r'^projects/$', 'all_projects', name='all_projects_view'),
    url(r'^projects/(?P<project_slug>\w+)/$', 'project', name='project_view'),
)

urlpatterns += patterns('editorsnotes.main.views.documents',
    url(r'^projects/(?P<project_slug>\w+)/documents/(?P<document_id>\d+)/transcript/$', 'transcript', name='transcript_view'),
    url(r'^projects/(?P<project_slug>\w+)/documents/(?P<document_id>\d+)/footnotes/(?P<footnote_id>\d+)/$', 'footnote', name='footnote_view'),
)
