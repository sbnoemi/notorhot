from django.conf.urls import patterns, include, url

from notorhot.views import CompetitionView, VoteView

urlpatterns = patterns('notorhot.views',    
    url(r'^$', CompetitionView.as_view(), name='notorhot_competition'),
    url(r'^vote/(?P<pk>\d+)/$', VoteView.as_view(), name='notorhot_vote'),
)
