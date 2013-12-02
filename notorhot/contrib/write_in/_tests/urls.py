from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'write-in/',  include('notorhot.contrib.write_in.urls')),
    url(r'',  include('notorhot.urls')),
)

