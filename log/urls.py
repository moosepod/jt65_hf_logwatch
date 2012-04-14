from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    (r'^$', 'log.views.callsigns'),
    (r'^callsigns/latest/$', 'log.views.latest_callsigns_json',{}, 'latest_callsigns_json'),
)
