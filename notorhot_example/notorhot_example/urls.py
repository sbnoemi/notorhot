from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'notorhot_example.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', RedirectView.as_view(url=reverse_lazy('notorhot_categories'))),
    url(r'^hot/', include('notorhot.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
