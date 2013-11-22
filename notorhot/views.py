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


class CompetitionView(NeverCacheMixin, WorkingSingleObjectMixin, CategoryMixin, 
        TemplateView):
    """
    Generates and displays a competition in the indicated category.
    """
    template_name = 'notorhot/competition.html'
    insufficient_data_template_name = 'notorhot/insufficient_data.html'
    http_method_names = ['get',]
    queryset = CandidateCategory.public.all()
    
    def get_category(self):
        return self.object
    
    def get_previous_vote(self):
        """
        If available, retrieves information saved in the session about the 
        last :class:`~notorhot.models.Competition` the user voted on.
        """
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
        """
        Adds new :class:`~notorhot.models.Competition` instance and (if 
        appropriate) previous vote data to context.
        """
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
    """
    Processes a vote on a :class:`~notorhot.models.Competition` and adds the 
    :class:`~notorhot.models.Competition` instance's ID to the session as 
    previous vote data (``reqest.session['last_vote_pk']``).
    """
    template_name = 'notorhot/already_voted.html'
    http_method_names = ['post',]
    form_class = VoteForm
    queryset = Competition.votable.all()
        
    def form_valid(self, form):
        """
        Saves vote; adds :class:`~notorhot.models.Competition` instance PK to 
        session as previous vote.
        
        .. note:: 
            This method swallows Competition.AlreadyVoted errors under the
            assumption that most are due to user error (clicking the form button 
            twice before the next page can load) rather than anything malicious.
            This behavior can be overridden by subclassing 
            :class:`~notorhot.views.VoteView`, overriding this method, and 
            hooking up the subclass to the urlconf (see :doc:`Extending NotorHot 
            documentation <../extending>`).
        """
        try:
            form.save()
        except Competition.AlreadyVoted:
            # if the competition's already been voted in, there's a pretty 
            # good chance this was just because the user double-clicked the 
            # submit button or something.  The most user-friendly thing to do
            # here is to swallow the error and just give them a new 
            # Competition anyway.
            pass
        else:
            # save in session for display on next competition
            self.request.session['last_vote_pk'] = self.object.pk
        return super(VoteView, self).form_valid(form)
    
    def get_form_kwargs(self):
        """
        Adds :class:`~notorhot.models.Competition` instance to keyword arguments
        used to initialize :class:`~notorhot.forms.VoteForm`.
        """
        if not self.object.category.is_public:
            raise Http404
            
        kwargs = super(VoteView, self).get_form_kwargs()
        kwargs.update({'competition': self.object})
        return kwargs
        
    def get_success_url(self):
        return self.object.category.get_absolute_url()
        

class CandidateView(SingleObjectTemplateResponseMixin, CategoryMixin, 
        BaseDetailView):
    """
    Displays details about a :class:`~notorhot.models.Candidate`.
    """
    template_name = 'notorhot/candidate.html'
    http_method_names = ['get',]    
    queryset = Candidate.enabled.all()
    context_object_name = 'candidate'
    
    def get_category(self):
        cat = self.object.category
        if not cat.is_public:
            raise Http404
        return cat
        

class LeaderboardView(CategoryMixin, TemplateView):
    """
    Displays leaderboard (list of :class:`~notorhot.models.Candidate` instnaces 
    with highest win percentage) for a category.
    """
    template_name = 'notorhot/leaders.html'
    http_method_names = ['get',]
    leaderboard_length = 10
    
    def get_category(self):
        cat = self._get_category()
        if not cat.is_public:
            raise Http404
        return cat    
    
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
    """
    Lists and links to :class:`~notorhot.models.CandidateCategory` instances 
    for which user can view and vote on competitions.
    """
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