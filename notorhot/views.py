from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.decorators.cache import never_cache

from notorhot.models import Competition, Candidate
from notorhot.utils import NeverCacheMixin

class CompetitionView(NeverCacheMixin, TemplateView):
    template_name = 'notorhot/competition.html'
    insufficient_data_template_name = 'notorhot/insufficient_data.html'
    http_method_names = ['get',]
    
    def get_context_data(self):
        context = super(CompetitionView, self).get_context_data()
        
        try:
            competition = Competition.objects.generate()
        except Candidate.DoesNotExist:
            # Not enough data.  Try again later
            self.template_name = self.insufficient_data_template_name
            return context
        
        context.update({
            'competition': competition,
        })        
        return context

def vote(request, competition_id):
    return HttpResponse('hi')