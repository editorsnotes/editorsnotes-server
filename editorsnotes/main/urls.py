from django.conf.urls.defaults import *

urlpatterns = patterns('mysite.polls.views',
    (r'^$', 'index'),
)
