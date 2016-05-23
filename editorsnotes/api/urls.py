# vim: set tw=0:

from django.conf.urls import url, include
from django.core.urlresolvers import RegexURLPattern
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token
from . import views


def format_patterns(urlpatterns):
    "If a URL pattern ends in a slash, it should be able to be rendered as different types"
    suffixes = ['json', 'jsonld', 'jsonld-browse', 'ttl', 'ttl-browse']
    ret = []
    for urlpattern in urlpatterns:
        if isinstance(urlpattern, RegexURLPattern):
            pattern = urlpattern.regex.pattern
            is_empty = pattern == '^$'

            if is_empty or pattern.endswith('/$'):
                regex = '^' if is_empty else urlpattern.regex.pattern[:-2]
                view = urlpattern._callback or urlpattern._callback_str
                kwargs = urlpattern.default_args
                name = urlpattern.name

                stripped_url = url(regex, view, kwargs, name)

                ret.append(format_suffix_patterns([stripped_url], True, suffixes)[0])
        ret.append(urlpattern)
    return ret


project_specific_patterns = [
    ### Project (general) ###
    url(r'^$', views.ProjectDetail.as_view(), name='projects-detail'),
    url(r'^vocab$', views.ProjectAPIDocumentation.as_view(), name='projects-api-documentation'),
    url(r'^activity/$', views.ActivityView.as_view(), name='projects-activity'),

    ### Topics ###
    url(r'^topics/$', views.TopicList.as_view(), name='topics-list'),
    url(r'^topics/(?P<pk>\d+)/$', views.TopicDetail.as_view(), name='topics-detail'),
    url(r'^topics/(?P<pk>\d+)/w/$', views.ENTopicDetail.as_view(), name='topics-wn-detail'),
    url(r'^topics/(?P<pk>\d+)/p/$', views.TopicLDDetail.as_view(), name='topics-proj-detail'),
    url(r'^topics/(?P<pk>\d+)/confirm_delete$', views.TopicConfirmDelete.as_view(), name='topics-confirm-delete'),

    ### Notes ###
    url(r'^notes/$', views.NoteList.as_view(), name='notes-list'),
    url(r'^notes/(?P<pk>\d+)/$', views.NoteDetail.as_view(), name='notes-detail'),
    url(r'^notes/(?P<pk>\d+)/confirm_delete$', views.NoteConfirmDelete.as_view(), name='notes-confirm-delete'),

    ### Documents ###
    url(r'^documents/$', views.DocumentList.as_view(), name='documents-list'),
    url(r'^documents/(?P<pk>\d+)/$', views.DocumentDetail.as_view(), name='documents-detail'),
    url(r'^documents/(?P<pk>\d+)/confirm_delete$', views.DocumentConfirmDelete.as_view(), name='documents-confirm-delete'),
    url(r'^documents/(?P<document_id>\d+)/scans/$', views.ScanList.as_view(), name='scans-list'),
    url(r'^documents/(?P<document_id>\d+)/scans/(?P<scan_id>\d+)/$', views.ScanDetail.as_view(), name='scans-detail'),

    url(r'^documents/(?P<document_id>\d+)/transcript/$', views.Transcript.as_view(), name='transcripts-detail'),
]

project_specific_patterns = format_patterns(project_specific_patterns)

urlpatterns = [
    url(r'^$', views.browse.root, name='root'),
    url(r'^browse/$', views.browse.browse_items, name='browse'),
    url(r'^auth-token/$', obtain_auth_token, name='obtain-auth-token'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^notes/$', views.AllProjectNoteList.as_view(), name='all-projects-notes-list'),
    url(r'^projects/$', views.ProjectList.as_view(), name='projects-list'),
    url(r'^projects/(?P<project_slug>[\w\-]+)/', include(project_specific_patterns)),
    url(r'^users/(?P<pk>\d+)/$', views.UserDetail.as_view(), name='users-detail'),
    url(r'^users/(?P<pk>\d+)/activity/$', views.ActivityView.as_view(), name='users-activity'),
    url(r'^me/$', views.SelfUserDetail.as_view(), name='users-detail-self'),
]

urlpatterns = format_patterns(urlpatterns)
