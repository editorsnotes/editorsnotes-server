# vim: set tw=0:

from django.conf.urls import patterns, url, include
import views

project_specific_patterns = patterns('',
    ### Project (general) ###
    url(r'^$', views.ProjectDetail.as_view(), name='api-project-detail'),
    url(r'^activity/$', views.ActivityView.as_view(), name='api-project-activity'),

    ### Topics ###
    url(r'^topics/$', views.TopicList.as_view(), name='api-topics-list'),
    url(r'^topics/(?P<topic_node_id>\d+)/$', views.TopicDetail.as_view(), name='api-topics-detail'),
    url(r'^topics/(?P<topic_node_id>\d+)/confirm_delete/$', views.TopicConfirmDelete.as_view(), name='api-topics-confirm-delete'),
    url(r'^topics/(?P<topic_node_id>\d+)/citations/$', views.TopicCitationList.as_view(), name='api-topic-citations-list'),
    url(r'^topics/(?P<topic_node_id>\d+)/citations/normalize_order/$', views.NormalizeCitationOrder.as_view(), name='api-topic-citations-normalize-order'),
    url(r'^topics/(?P<topic_node_id>\d+)/citations/(?P<citation_id>\d+)/$', views.TopicCitationDetail.as_view(), name='api-topic-citations-detail'),

    ### Notes ###
    url(r'^notes/$', views.NoteList.as_view(), name='api-notes-list'),
    url(r'^notes/(?P<pk>\d+)/$', views.NoteDetail.as_view(), name='api-notes-detail'),
    url(r'^notes/(?P<pk>\d+)/confirm_delete/$', views.NoteConfirmDelete.as_view(), name='api-notes-confirm-delete'),

    ### Documents ###
    url(r'^documents/$', views.DocumentList.as_view(), name='api-documents-list'),
    url(r'^documents/(?P<pk>\d+)/$', views.DocumentDetail.as_view(), name='api-documents-detail'),
    url(r'^documents/(?P<pk>\d+)/confirm_delete/$', views.DocumentConfirmDelete.as_view(), name='api-documents-confirm-delete'),
    url(r'^documents/(?P<document_id>\d+)/scans/$', views.ScanList.as_view(), name='api-scans-list'),
    url(r'^documents/(?P<document_id>\d+)/scans/(?P<scan_id>\d+)/$', views.ScanDetail.as_view(), name='api-scans-detail'),
    url(r'^documents/(?P<document_id>\d+)/scans/normalize_order/$', views.NormalizeScanOrder.as_view(), name='api-scans-normalize-order'),

    url(r'^documents/(?P<document_id>\d+)/transcript/$', views.Transcript.as_view(), name='api-transcripts-detail'),
)

urlpatterns = patterns('',
    url(r'^$', views.base.root, name='api-root'),
    url(r'^auth-token/$', 'rest_framework.authtoken.views.obtain_auth_token', name='obtain-auth-token'),
    url(r'^search/$', views.SearchView.as_view(), name='api-search'),
    url(r'^topics/$', views.TopicNodeList.as_view(), name='api-topic-nodes-list'),
    url(r'^topics/(?P<pk>\d+)/$$', views.TopicNodeDetail.as_view(), name='api-topic-nodes-detail'),
    url(r'^projects/$', views.ProjectList.as_view(), name='api-projects-list'),
    url(r'^projects/(?P<project_slug>\w+)/', include(project_specific_patterns)),
)
