import datetime
from mock import Mock, patch

from django.test import TestCase
from django.forms import ValidationError

from notorhot._tests.factories import mixer
from notorhot._tests._utils import setup_view, ViewTestMixin
from notorhot.models import CandidateCategory, Candidate, Competition
from notorhot.views import CompetitionView, VoteView, CandidateView, \
    LeaderboardView, CategoryListView


class CompetitionViewTestCase(ViewTestMixin, TestCase):
    view_class = CompetitionView
    
    def test_get_category(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        view = self.make_view('get', view_kwargs={ 'object': cat, })
        
        view_cat = view.get_category()
        self.assertEqual(view_cat, cat)
    
    def test_get_previous_vote(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        
        # last vote omitted
        view = self.make_view('get', view_kwargs={ 'object': cat, }, 
            session_data={})
        previous = view.get_previous_vote()
        self.assertIsNone(previous)
    
        # last vote not found
        view = self.make_view('get', view_kwargs={ 'object': cat, }, 
            session_data={ 'last_vote_pk': 123, })
        previous = view.get_previous_vote()
        self.assertIsNone(previous)
        
        # last vote found
        comp = mixer.blend('notorhot.Competition')
        view = self.make_view('get', view_kwargs={ 'object': cat, }, 
            session_data={ 'last_vote_pk': comp.id, })
        previous = view.get_previous_vote()
        self.assertEqual(previous, comp)        
        
    def test_generate_competition(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        mixer.cycle(4).blend('notorhot.Candidate', category=cat)
        view = self.make_view('get', view_kwargs={ 'object': cat, })
        
        num_comps = Competition.objects.count()
        
        comp = view.generate_competition()
        
        self.assertEqual(comp.category, cat)
        self.assertEqual(Competition.objects.count(), num_comps + 1)
        
    def test_get_context_data(self):
        cat = mixer.blend('notorhot.CandidateCategory')

        view = self.make_view('get', view_kwargs={ 'object': cat, }, 
            session_data={})
        context = view.get_context_data()
        
        self.assertEqual(view.template_name, 'notorhot/insufficient_data.html')
        self.assertFalse('competition' in context)
        self.assertFalse('previous_vote' in context)

        mixer.cycle(4).blend('notorhot.Candidate', category=cat)        
        view = self.make_view('get', view_kwargs={ 'object': cat, }, 
            session_data={})
        context = view.get_context_data()
        
        self.assertEqual(view.template_name, 'notorhot/competition.html')
        self.assertTrue('competition' in context)
        self.assertTrue('previous_vote' in context)


class VoteViewTestCase(TestCase):
    pass


class CandidateViewTestCase(TestCase):
    pass


class LeaderboardViewTestCase(TestCase):
    pass


class CategoryListViewTestCase(TestCase):
    pass