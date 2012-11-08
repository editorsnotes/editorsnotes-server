from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^main/project/(?P<project_id>\d+)/$', 'change_project', name='project_edit_view'),
    url(r'^main/project/(?P<project_id>\d+)/roster/$', 'project_roster', name='project_roster_view'),
    url(r'^main/project/(?P<project_id>\d+)/featured_items/$', 'change_featured_items', name='change_featured_items_view'),
    url(r'^main/topic/add/$', views.TopicAdminView.as_view(), name='admin:main_topic_add'),
    url(r'^main/topic/(?P<topic_id>\d+)/$', views.TopicAdminView.as_view(), name='admin:main_topic_change'),
    url(r'^main/document/add/$', views.DocumentAdminView.as_view(), name='admin:main_document_add'),
    url(r'^main/document/(?P<document_id>\d+)/$', views.DocumentAdminView.as_view(), name='admin:main_document_change'),
    url(r'^main/note/add/$', views.NoteAdminView.as_view(), name='admin:main_note_add'),
    url(r'^main/note/(?P<note_id>\d+)/$', views.NoteAdminView.as_view(), name='admin:main_note_change'),
    url(r'^main/note/(?P<note_id>\d+)/sections/$', views.note_sections, name='note_sections'),
)
