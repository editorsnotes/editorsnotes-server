# vim: set tw=0:

from django.conf.urls import patterns, url, include
from django.core.urlresolvers import RegexURLPattern
from rest_framework.urlpatterns import format_suffix_patterns
import views

def format_patterns(urlpatterns):
    "If a URL pattern ends in a slash, it should be able to be rendered as different types"
    suffixes = ['json', 'html', 'api']
    ret = []
    for urlpattern in urlpatterns:
        if isinstance(urlpattern, RegexURLPattern) and urlpattern.regex.pattern.endswith('/$'):
            regex = urlpattern.regex.pattern[:-2]
            view = urlpattern._callback or urlpattern._callback_str
            kwargs = urlpattern.default_args
            name = urlpattern.name

            stripped_url = url(regex, view, kwargs, name)

            ret.append(format_suffix_patterns([stripped_url], True, suffixes)[0])
        ret.append(urlpattern)
    return ret

project_specific_patterns = patterns('',
    ### Project (general) ###
    url(r'^/$', views.ProjectDetail.as_view(), name='projects-detail'),
    url(r'^/activity/$', views.ActivityView.as_view(), name='projects-activity'),

    ### Topics ###
    url(r'^/topics/$', views.TopicList.as_view(), name='topics-list'),
    url(r'^/topics/(?P<topic_node_id>\d+)/$', views.TopicDetail.as_view(), name='topics-detail'),
    url(r'^/topics/(?P<topic_node_id>\d+)/confirm_delete$', views.TopicConfirmDelete.as_view(), name='topics-confirm-delete'),
    url(r'^/topics/(?P<topic_node_id>\d+)/citations/$', views.TopicCitationList.as_view(), name='topic-citations-list'),
    url(r'^/topics/(?P<topic_node_id>\d+)/citations/normalize_order$', views.NormalizeCitationOrder.as_view(), name='topic-citations-normalize-order'),
    url(r'^/topics/(?P<topic_node_id>\d+)/citations/(?P<citation_id>\d+)/$', views.TopicCitationDetail.as_view(), name='topic-citations-detail'),

    ### Notes ###
    url(r'^/notes/$', views.NoteList.as_view(), name='notes-list'),
    url(r'^/notes/(?P<pk>\d+)/$', views.NoteDetail.as_view(), name='notes-detail'),
    url(r'^/notes/(?P<pk>\d+)/confirm_delete$', views.NoteConfirmDelete.as_view(), name='notes-confirm-delete'),

    ### Documents ###
    url(r'^/documents/$', views.DocumentList.as_view(), name='documents-list'),
    url(r'^/documents/(?P<pk>\d+)/$', views.DocumentDetail.as_view(), name='documents-detail'),
    url(r'^/documents/(?P<pk>\d+)/confirm_delete$', views.DocumentConfirmDelete.as_view(), name='documents-confirm-delete'),
    url(r'^/documents/(?P<document_id>\d+)/scans/$', views.ScanList.as_view(), name='scans-list'),
    url(r'^/documents/(?P<document_id>\d+)/scans/(?P<scan_id>\d+)/$', views.ScanDetail.as_view(), name='scans-detail'),
    url(r'^/documents/(?P<document_id>\d+)/scans/normalize_order$', views.NormalizeScanOrder.as_view(), name='scans-normalize-order'),

    url(r'^/documents/(?P<document_id>\d+)/transcript/$', views.Transcript.as_view(), name='transcripts-detail'),
)
project_specific_patterns = format_patterns(project_specific_patterns)

urlpatterns = patterns('',
    url(r'^/$', views.base.root, name='root'),
    url(r'^auth-token/$', 'rest_framework.authtoken.views.obtain_auth_token', name='obtain-auth-token'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^topics/$', views.TopicNodeList.as_view(), name='topic-nodes-list'),
    url(r'^topics/(?P<pk>\d+)/$$', views.TopicNodeDetail.as_view(), name='topic-nodes-detail'),
    url(r'^projects/$', views.ProjectList.as_view(), name='projects-list'),
    url(r'^projects/(?P<project_slug>\w+)', include(project_specific_patterns)),
    url(r'^users/(?P<username>[\w@\+\.\-]+)/$', views.UserDetail.as_view(), name='users-detail'),

)

urlpatterns = format_patterns(urlpatterns)
