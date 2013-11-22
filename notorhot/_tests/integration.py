import datetime
from mock import Mock, patch

from django.test import TestCase
from django.forms import ValidationError

from notorhot._tests.factories import mixer
from notorhot._tests._utils import setup_view, ViewTestMixin, \
    generate_leaderboard_data
from notorhot.models import CandidateCategory, Candidate, Competition
from notorhot.forms import VoteForm
from notorhot.views import CompetitionView, VoteView, CandidateView, \
    LeaderboardView, CategoryListView


class URLConfMixin(object):
    urls = 'notorhot._tests.urls'


class AbsoluteURLTestCase(URLConfMixin, TestCase):
    def test_get_urls(self):
        cat = mixer.blend('notorhot.CandidateCategory', slug='cat-slug')
        self.assertEqual(cat.get_absolute_url(), '/cat-slug/')
        self.assertEqual(cat.get_leaderboard_url(), '/cat-slug/leaders/')
        
        cand = mixer.blend('notorhot.Candidate', slug='cand-slug', category=cat)
        self.assertEqual(cand.get_absolute_url(), '/candidate/cat-slug/cand-slug/')


class CompetitionViewTestCase(URLConfMixin, TestCase):
    def test_success(self):
        cat = mixer.blend('notorhot.CandidateCategory', slug='cat-slug')
        mixer.blend('notorhot.CandidateCategory')
        cand1 = mixer.blend('notorhot.Candidate', category=cat, name='Alpha')
        cand2 = mixer.blend('notorhot.Candidate', category=cat, name='Beta')
        
        response = self.client.get('/cat-slug/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], CompetitionView)
        self.assertIsNotNone(response.context['competition'])
        self.assertEqual(response.context['competition'].category, cat)
        self.assertEqual(response.context['category'], cat)
        self.assertContains(response, 'Alpha')
        self.assertContains(response, 'Beta')
        self.assertTemplateUsed(response, 'notorhot/competition.html')
        
    def test_insufficient_data(self):
        cat = mixer.blend('notorhot.CandidateCategory', slug='cat-slug')
        mixer.blend('notorhot.CandidateCategory')
        cand1 = mixer.blend('notorhot.Candidate', category=cat, name='Alpha')
        
        response = self.client.get('/cat-slug/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], CompetitionView)
        self.assertNotIn('competition', response.context)
        self.assertNotIn('Alpha', response)
        self.assertNotIn('Beta', response)
        self.assertTemplateUsed(response, 'notorhot/insufficient_data.html')


class VoteViewTestCase(URLConfMixin, TestCase):
    def test_success(self):
        cat = mixer.blend('notorhot.CandidateCategory', slug='cat-slug')
        cand1 = mixer.blend('notorhot.Candidate', category=cat, name='Alpha')
        cand2 = mixer.blend('notorhot.Candidate', category=cat, name='Beta')
        comp = mixer.blend('notorhot.Competition', left=cand1, right=cand2, 
            category=cat, id=1)
        
        response = self.client.post('/vote/1/', follow=False,
            data={ 'winner': Competition.SIDES.LEFT, })
            
        the_comp = Competition.objects.get(id=1)
            
        self.assertEqual(response.status_code, 302)
        self.assertEqual(the_comp.winner, cand1)
        self.assertEqual(the_comp.winning_side, Competition.SIDES.LEFT)
        self.assertIsNotNone(the_comp.date_voted)
        self.assertRedirects(response, '/cat-slug/')
        
    def test_invalid_answer(self):
        cat = mixer.blend('notorhot.CandidateCategory', slug='cat-slug')
        cand1 = mixer.blend('notorhot.Candidate', category=cat, name='Alpha')
        cand2 = mixer.blend('notorhot.Candidate', category=cat, name='Beta')
        comp = mixer.blend('notorhot.Competition', left=cand1, right=cand2, 
            category=cat, id=1)
        
        response = self.client.post('/vote/1/', follow=False,
            data={ 'winner': 99, })

        the_comp = Competition.objects.get(id=1)
            
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(the_comp.winner)
        self.assertIsNone(the_comp.winning_side)
        self.assertIsNone(the_comp.date_voted)
        self.assertIsInstance(response.context['form'], VoteForm)
        self.assertIsInstance(response.context['view'], VoteView)
        self.assertTemplateUsed(response, 'notorhot/already_voted.html')
        
    def test_already_voted(self):
        cat = mixer.blend('notorhot.CandidateCategory', slug='cat-slug')
        cand1 = mixer.blend('notorhot.Candidate', category=cat, name='Alpha')
        cand2 = mixer.blend('notorhot.Candidate', category=cat, name='Beta')
        comp = mixer.blend('notorhot.Competition', left=cand1, right=cand2, 
            category=cat, id=1, date_voted=mixer.fake)
        
        response = self.client.post('/vote/1/', follow=False,
            data={ 'winner': Competition.SIDES.LEFT, })
            
        self.assertEqual(response.status_code, 404)
    

class CandidateViewTestCase(URLConfMixin, TestCase):
    def test_success(self):
        cat = mixer.blend('notorhot.CandidateCategory', slug='cat-slug')
        cand = mixer.blend('notorhot.Candidate', category=cat, name='Alpha', slug='alpha')

        response = self.client.get('/candidate/cat-slug/alpha/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], CandidateView)
        self.assertIsNotNone(response.context['candidate'])
        self.assertEqual(response.context['candidate'], cand)
        self.assertIsNotNone(response.context['category'])
        self.assertEqual(response.context['category'], cat)
        self.assertContains(response, 'Alpha')
        self.assertTemplateUsed(response, 'notorhot/candidate.html')


class LeaderboardViewTestCase(URLConfMixin, TestCase):
    def test_success(self):
        cat1 = mixer.blend('notorhot.CandidateCategory', slug='cat-slug')
        cat2 = mixer.blend('notorhot.CandidateCategory')        
        (cand1, cand2, cand3, cand4) = generate_leaderboard_data(cat1, cat2)

        with patch.object(LeaderboardView, 'leaderboard_length', new=3):
            response = self.client.get('/cat-slug/leaders/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], LeaderboardView)
        self.assertIsNotNone(response.context['leaders'])
        self.assertEqual(list(response.context['leaders']), [cand4, cand3, cand2])
        self.assertIsNotNone(response.context['category'])
        self.assertEqual(response.context['category'], cat1)
        self.assertContains(response, 'Beta')
        self.assertContains(response, 'Gamma')
        self.assertContains(response, 'Delta')
        self.assertTemplateUsed(response, 'notorhot/leaders.html')
        
    def test_empty(self):
        cat1 = mixer.blend('notorhot.CandidateCategory', slug='cat-slug')

        response = self.client.get('/cat-slug/leaders/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], LeaderboardView)
        self.assertIsNotNone(response.context['leaders'])
        self.assertEqual(len(response.context['leaders']), 0)
        self.assertIsNotNone(response.context['category'])
        self.assertEqual(response.context['category'], cat1)
        self.assertNotContains(response, 'Beta')
        self.assertNotContains(response, 'Gamma')
        self.assertTemplateUsed(response, 'notorhot/leaders.html')
        

class CategoryListViewTestCase(URLConfMixin, TestCase):
    def test_success(self):
        cat1 = mixer.blend('notorhot.CandidateCategory', name='Alpha')
        cat2 = mixer.blend('notorhot.CandidateCategory', name='Beta')    
        cat3 = mixer.blend('notorhot.CandidateCategory', name='Gamma', 
            is_public=False)        

        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], CategoryListView)
        self.assertIsNotNone(response.context['categories'])
        self.assertItemsEqual(response.context['categories'], [cat1, cat2])
        self.assertContains(response, 'Alpha')
        self.assertContains(response, 'Beta')
        self.assertNotContains(response, 'Gamma')
        self.assertTemplateUsed(response, 'notorhot/categories.html')
        
    def test_empty(self):
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], CategoryListView)
        self.assertIsNotNone(response.context['categories'])
        self.assertEqual(len(response.context['categories']), 0)
        self.assertNotContains(response, 'Alpha')
        self.assertNotContains(response, 'Beta')
        self.assertNotContains(response, 'Gamma')
        self.assertTemplateUsed(response, 'notorhot/categories.html')
    