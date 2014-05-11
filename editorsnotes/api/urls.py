# vim: set tw=0:

from django.conf.urls import patterns, url, include
import views

project_specific_patterns = patterns('',
    url(r'^$', views.ProjectDetail.as_view(), name='api-project-detail'),
    url(r'^activity/$', views.ActivityView.as_view(), name='api-project-activity'),
    url(r'^topics/$', views.TopicList.as_view(), name='api-topics-list'),
    url(r'^topics/(?P<topic_node_id>\d+)/$', views.TopicDetail.as_view(), name='api-topics-detail'),
    url(r'^topics/(?P<topic_node_id>\d+)/citations/$', views.TopicCitationList.as_view(), name='api-topic-citations-list'),
    url(r'^topics/(?P<topic_node_id>\d+)/citations/(?P<citation_id>\d+)/$', views.TopicCitationDetail.as_view(), name='api-topic-citations-detail'),
    url(r'^notes/$', views.NoteList.as_view(), name='api-notes-list'),
    url(r'^notes/(?P<pk>\d+)/$', views.NoteDetail.as_view(), name='api-notes-detail'),
    url(r'^notes/(?P<note_id>\d+)/s(?P<section_id>\d+)/$', views.NoteSectionDetail.as_view(), name='api-notes-section-detail'),
    url(r'^notes/(?P<pk>\d+)/normalize_section_order/$', views.normalize_section_order, name='api-notes-normalize-section-order'),
    url(r'^documents/$', views.DocumentList.as_view(), name='api-documents-list'),
    url(r'^documents/(?P<pk>\d+)/$', views.DocumentDetail.as_view(), name='api-documents-detail'),
    url(r'^documents/(?P<document_id>\d+)/scans/$', views.ScanList.as_view(), name='api-scans-list'),
    url(r'^documents/(?P<document_id>\d+)/scans/(?P<scan_id>\d+)/$', views.ScanDetail.as_view(), name='api-scans-detail'),
    url(r'^documents/(?P<document_id>\d+)/scans/normalize_order/$', views.normalize_scan_order, name='api-scans-normalize-order'),
)

urlpatterns = patterns('',
    url(r'^$', views.base.root, name='api-root'),
    url(r'^auth-token/$', 'rest_framework.authtoken.views.obtain_auth_token', name='obtain-auth-token'),
    url(r'^search/$', views.SearchView.as_view(), name='api-search'),
    url(r'^topics/$', views.TopicNodeList.as_view(), name='api-topic-nodes-list'),
    url(r'^topics/(?P<pk>\d+)/$$', views.TopicNodeDetail.as_view(), name='api-topic-nodes-list'),
    url(r'^projects/$', views.ProjectList.as_view(), name='api-projects-list'),
    url(r'^projects/(?P<project_slug>\w+)/', include(project_specific_patterns)),
)
