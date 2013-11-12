from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView, BaseDetailView, \
    SingleObjectTemplateResponseMixin
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse_lazy

from notorhot.models import Competition, Candidate, CandidateCategory
from notorhot.forms import VoteForm
from notorhot.utils import NeverCacheMixin, WorkingSingleObjectMixin, \
    CategoryMixin


class CompetitionView(NeverCacheMixin, WorkingSingleObjectMixin, CategoryMixin, TemplateView):
    template_name = 'notorhot/competition.html'
    insufficient_data_template_name = 'notorhot/insufficient_data.html'
    http_method_names = ['get',]
    queryset = CandidateCategory.public.all()
    
    def get_category(self):
        return self.object
    
    def get_previous_vote(self):
        previous = None
        previous_pk = self.request.session.get('last_vote_pk')
        
        if previous_pk is not None:
            try:
                previous = Competition.objects.get(pk=previous_pk)
            except Competition.DoesNotExist:
                pass
        
        return previous
        
    def generate_competition(self):
        return self.object.generate_competition()
    
    def get_context_data(self, *args, **kwargs):
        context = super(CompetitionView, self).get_context_data(*args, **kwargs)
        
        try:
            competition = self.generate_competition()
        except Candidate.DoesNotExist:
            # Not enough data.  Try again later.
            self.template_name = self.insufficient_data_template_name
            return context
        
        context.update({
            'competition': competition,
            'previous_vote': self.get_previous_vote(),
        })        
        return context

# This might be simpler as an UpdateView, except that the form isn't a ModelForm.
# Oh well.
class VoteView(NeverCacheMixin, WorkingSingleObjectMixin, FormView):
    template_name = 'notorhot/already_voted.html'
    http_method_names = ['post',]
    form_class = VoteForm
    queryset = Competition.votable.all()
        
    def form_valid(self, form):
        form.save()
        # save in session for display on next competition
        self.request.session['last_vote_pk'] = self.object.pk
        return super(VoteView, self).form_valid(form)
    
    def get_form_kwargs(self):        
        kwargs = super(VoteView, self).get_form_kwargs()
        kwargs.update({'competition': self.object})
        return kwargs
        
    def get_success_url(self):
        return self.object.category.get_absolute_url()
        

class CandidateView(SingleObjectTemplateResponseMixin, CategoryMixin, BaseDetailView):
    template_name = 'notorhot/candidate.html'
    http_method_names = ['get',]    
    queryset = Candidate.enabled.all()
    context_object_name = 'candidate'
    
    def get_category(self):
        return self.object.category
        

class LeaderboardView(CategoryMixin, TemplateView):
    template_name = 'notorhot/leaders.html'
    http_method_names = ['get',]
    leaderboard_length = 10
    
    def get_category(self):
        return self._get_category()
    
    def get_leaders(self):
        return Candidate.enabled.for_category(self.category).order_by_wins(
            )[:self.leaderboard_length]
    
    def get_context_data(self, *args, **kwargs):
        context = super(LeaderboardView, self).get_context_data()
        
        context.update({
            'leaders': self.get_leaders()
        })
        
        return context
    
    
class CategoryListView(TemplateView):
    template_name = 'notorhot/categories.html'
    http_method_names = ['get',]
    
    def get_categories(self):
        return CandidateCategory.public.all()
    
    def get_context_data(self, *args, **kwargs):
        context = super(CategoryListView, self).get_context_data()
        
        context.update({
            'categories': self.get_categories()
        })
        
        return context