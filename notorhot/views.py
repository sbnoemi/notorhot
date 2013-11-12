from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse_lazy

from notorhot.models import Competition, Candidate
from notorhot.forms import VoteForm
from notorhot.utils import NeverCacheMixin, ExecutableQuerysetMixin


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


class VoteView(NeverCacheMixin, ExecutableQuerysetMixin, SingleObjectMixin, 
        FormView):
    template_name = 'notorhot/already_voted.html'
    http_method_names = ['post',]
    form_class = VoteForm
    queryset_executable = Competition.votable.all
    success_url = reverse_lazy('notorhot_competition')
    
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super(VoteView, self).dispatch(*args, **kwargs)
        
    def form_valid(self, form):
        form.save()
        return super(VoteView, self).form_valid(form)
    
    def get_form_kwargs(self):        
        kwargs = super(VoteView, self).get_form_kwargs()
        competition = self.get_object()
        kwargs.update({'competition': competition})
        return kwargs