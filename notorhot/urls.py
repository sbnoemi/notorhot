from django.conf.urls import patterns, include, url

from notorhot.views import CompetitionView, VoteView, LeaderboardView, \
    CandidateView

urlpatterns = patterns('notorhot.views',    
    url(r'^$', CompetitionView.as_view(), name='notorhot_competition'),
    url(r'^vote/(?P<pk>\d+)/$', VoteView.as_view(), name='notorhot_vote'),
    url(r'^candidate/(?P<slug>[\w-]+)/$', CandidateView.as_view(), 
        name='notorhot_candidate'),
    url(r'^leaders/$', LeaderboardView.as_view(), name='notorhot_leaders'),
)
