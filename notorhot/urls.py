from django.conf.urls import patterns, include, url

from notorhot.views import CompetitionView

urlpatterns = patterns('notorhot.views',    
    url(r'^$', CompetitionView.as_view(), name='notorhot_competition'),
    url(r'^vote/(?P<competition_id>\d+)/$', 'vote', name='notorhot_vote'),
)
