import datetime

from django.test import TestCase

from notorhot._tests.factories import mixer
from notorhot.models import CandidateCategory, Candidate, Competition

class NotorHotCategoryTestCase(TestCase):
    def test_category_publicity_manager(self):
        mixer.blend('notorhot.CandidateCategory', is_public=True)
        mixer.blend('notorhot.CandidateCategory', is_public=False)
        self.assertEqual(CandidateCategory.objects.count(), 2)
        self.assertEqual(CandidateCategory.public.count(), 1)

    def test_category_competition_generator(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        enabled = mixer.cycle(3).blend('notorhot.Candidate', category=cat, is_enabled=True)
        disabled = mixer.cycle(2).blend('notorhot.Candidate', category=cat, is_enabled=False)
        
        comp = cat.generate_competition()
        self.assertTrue(comp.left in enabled)
        self.assertTrue(comp.right in enabled)
        self.assertEqual(comp.category, cat)
        
    def test_category_num_candidates(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        mixer.cycle(3).blend('notorhot.Candidate', category=cat, is_enabled=True)
        mixer.cycle(2).blend('notorhot.Candidate', category=cat, is_enabled=False)
        self.assertEqual(cat.num_candidates, 3)
        
    def test_category_num_voted_comps(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        mixer.cycle(3).blend('notorhot.Competition', category=cat, date_voted=None)
        mixer.cycle(2).blend('notorhot.Competition', category=cat, 
            date_voted=datetime.datetime.now())
        self.assertEqual(cat.num_voted_competitions, 2)
        
    
class NotorHotCandidateTestCase(TestCase):
    pass
    
    
class NotorHotCompetitionTestCase(TestCase):
    pass