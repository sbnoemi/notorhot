from django.conf.urls import patterns, include, url

from notorhot.contrib.write_in.views import WriteInDefaultView

urlpatterns = patterns('',    
    url(r'^$', WriteInDefaultView.as_view(), name='write_in_submit'),
)
