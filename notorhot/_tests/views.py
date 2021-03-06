import datetime
from mock import Mock, patch, MagicMock, PropertyMock

from django.test import TestCase
from django.forms import ValidationError
from django.http import Http404

from notorhot._tests.factories import mixer
from notorhot._tests._utils import setup_view, ViewTestMixin, \
    generate_leaderboard_data
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


class VoteViewTestCase(ViewTestMixin, TestCase):
    view_class = VoteView
    
    def test_form_valid(self):
        comp = mixer.blend('notorhot.Competition')
        form = Mock()
        view = self.make_view('post', view_kwargs={ 'object': comp, }, 
            session_data={})
        
        resp = view.form_valid(form)
        self.assertEqual(form.save.call_count, 1)
        self.assertEqual(view.request.session['last_vote_pk'], comp.id)
                
        comp2 = mixer.blend('notorhot.Competition', date_voted=mixer.fake)
        form = MagicMock()
        type(form).save = PropertyMock(side_effect=Competition.AlreadyVoted)
        view = self.make_view('post', view_kwargs={ 'object': comp2, }, 
            session_data={})
        
        try:
            resp = view.form_valid(form)
        except Competition.AlreadyVoted:
            self.fail("VoteView.form_valid() should swallow "
                "Competition.AlreadyVoted exceptions")
        
        
    def test_get_form_kwargs(self):
        comp = mixer.blend('notorhot.Competition')
        view = self.make_view('post', view_kwargs={ 'object': comp, })
        
        kwargs = view.get_form_kwargs()
        self.assertTrue('competition' in kwargs)
        self.assertEqual(kwargs['competition'], comp)
        
        cat = mixer.blend('notorhot.CandidateCategory', is_public=False)
        comp2 = mixer.blend('notorhot.Competition', category=cat)
        view = self.make_view('post', view_kwargs={ 'object': comp2, })
        
        with self.assertRaises(Http404):
            view.get_form_kwargs()
        
        
    def test_get_success_url(self):
        comp = mixer.blend('notorhot.Competition')
        view = self.make_view('post', view_kwargs={ 'object': comp, })
        
        with patch.object(comp.category, 'get_absolute_url') as mock_get_url:
            mock_get_url.return_value = '/a/url/'
            success_url = view.get_success_url()
            
            self.assertEqual(mock_get_url.call_count, 1)
            self.assertEqual(success_url, '/a/url/')


class CandidateViewTestCase(ViewTestMixin, TestCase):
    view_class = CandidateView

    def test_get_category(self):
        cats = mixer.cycle(2).blend('notorhot.CandidateCategory')
        cand = mixer.blend('notorhot.Candidate', category=cats[0])
        view = self.make_view('get', view_kwargs={ 'object': cand, })
        
        cat = view.get_category()
        self.assertEqual(cat, cats[0])
        
        cat = mixer.blend('notorhot.CandidateCategory', is_public=False)
        cand = mixer.blend('notorhot.Candidate', category=cat)
        view = self.make_view('get', view_kwargs={ 'object': cand, })
        
        with self.assertRaises(Http404):
            view.get_category()


class LeaderboardViewTestCase(ViewTestMixin, TestCase):
    view_class = LeaderboardView
    
    def test_get_category(self):
        cat1 = mixer.blend('notorhot.CandidateCategory')
        view = self.make_view('get', request_kwargs={ 'category_slug': cat1.slug, })
        
        view_cat = view.get_category()
        self.assertEqual(view_cat, cat1)
        
        cat2 = mixer.blend('notorhot.CandidateCategory', is_public=False)
        cand = mixer.blend('notorhot.Candidate', category=cat2)
        view = self.make_view('get', request_kwargs={ 'category_slug': cat2.slug, })
        
        with self.assertRaises(Http404):
            view.get_category()
        
    def test_get_leaders(self):
        cat1 = mixer.blend('notorhot.CandidateCategory')
        cat2 = mixer.blend('notorhot.CandidateCategory')
        
        (cand1, cand2, cand3, cand4) = generate_leaderboard_data(cat1, cat2)

        view = self.make_view('get', view_kwargs={ 'leaderboard_length': 3 },
            request_kwargs={ 'category_slug': cat1.slug, })
        
        leaders = view.get_leaders()
        self.assertEqual(list(leaders), [cand4, cand3, cand2,])

        
    def test_get_context_data(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        view = self.make_view('get', request_kwargs={ 'category_slug': cat.slug, })

        with patch.object(self.view_class, 'get_leaders') as mock_get_leaders:
            mock_get_leaders.return_value = ['leader_list',]
            
            context = view.get_context_data()
            
            self.assertTrue('leaders' in context)
            self.assertEqual(context['leaders'], ['leader_list',])


class CategoryListViewTestCase(ViewTestMixin, TestCase):
    view_class = CategoryListView
    
    def test_get_categories(self):
        cat1 = mixer.blend('notorhot.CandidateCategory')
        cat2 = mixer.blend('notorhot.CandidateCategory')
        cat3 = mixer.blend('notorhot.CandidateCategory', is_public=False)
        view = self.make_view('get')
        
        view_cats = view.get_categories()
        self.assertItemsEqual(view_cats, (cat1, cat2))
        
    def test_get_context_data(self):
        view = self.make_view('get')

        with patch.object(self.view_class, 'get_categories') as mock_get_categories:
            mock_get_categories.return_value = ['category_list',]
            
            context = view.get_context_data()
            
            self.assertTrue('categories' in context)
            self.assertEqual(context['categories'], ['category_list',])
