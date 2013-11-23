from copy import copy

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _, ugettext_lazy as _l
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import View, TemplateView
from django.conf import settings

from notorhot.contrib.write_in.utils import get_write_in_model, \
    get_write_in_model_name, RichFormFactoryCreateView


# Create your views here.
class WriteInBaseView(RichFormFactoryCreateView):
    allowed_methods = ['get', 'post',]
    model = get_write_in_model()
    template_name_suffix = '_create'
        
        
class WriteInDefaultView(WriteInBaseView):
    default_fields = [
            'submitter_name', 'submitter_email', 'candidate_name', 
        ]
    labels = {
            'submitter_name': _l(u"Your Name"),
            'submitter_email': _l(u"Your Email"),
        }
    success_url = reverse_lazy('write_in_thanks')
    
    def __init__(self, *args, **kwargs):
        
        # If we're using the default model, we can specify our fields explicitly
        # if they haven't been explicitly overridden
        if getattr(self, 'fields', None) is None and \
                get_write_in_model_name() == 'write_in.DefaultWriteIn':
            self.fields = self.default_fields
        
        # and otherwise, let's assume we're using a subclass of BaseWriteIn and
        # make sure we hide programmatically-populated fields
        elif getattr(self, 'exclude_fields', None) is None:
            self.exclude_fields = ['date_submitted', 'date_processed', 'status',]
            
        super(WriteInDefaultView, self).__init__(*args, **kwargs)
            
        
        
class WriteInThanksView(View):
    def dispatch(self, *args, **kwargs):
        return HttpResponse('thanks')