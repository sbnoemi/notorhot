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
    def test_order_by_wins(self):
        # test ordered by % wins, not # wins
        mixer.blend('notorhot.Candidate', votes=18, wins=9) # .5
        mixer.blend('notorhot.Candidate', votes=15, wins=8) # .5333
        mixer.blend('notorhot.Candidate', votes=12, wins=7) # .58333
        mixer.blend('notorhot.Candidate', votes=9, wins=6) # .6667
            
        in_order = Candidate.objects.all().order_by_wins()
        # get win count for ordered candidates = should be 6, 7, 8, 9
        wins = [c.wins for c in in_order]
        self.assertEqual(wins, [6, 7, 8, 9])
        
    def test_for_category(self):
        cat1 = mixer.blend('notorhot.CandidateCategory')
        cat2 = mixer.blend('notorhot.CandidateCategory')
        mixer.cycle(3).blend('notorhot.Candidate', category=cat1)
        mixer.cycle(2).blend('notorhot.Candidate', category=cat2)
        
        self.assertEqual(Candidate.objects.for_category(cat1).count(), 3)
        
    def test_enabled(self):
        mixer.cycle(3).blend('notorhot.Candidate', is_enabled=True)
        mixer.cycle(2).blend('notorhot.Candidate', is_enabled=False)
        
        self.assertEqual(Candidate.enabled.count(), 3)
        
    def test_manger_and_queryset_chaining(self):
        cat1 = mixer.blend('notorhot.CandidateCategory')
        cat2 = mixer.blend('notorhot.CandidateCategory')
        mixer.blend('notorhot.Candidate', votes=18, wins=9, category=cat1, is_enabled=True) # .5
        mixer.blend('notorhot.Candidate', votes=15, wins=8, category=cat1, is_enabled=True) # .5333
        mixer.blend('notorhot.Candidate', votes=12, wins=7, category=cat1, is_enabled=True) # .58333
        mixer.blend('notorhot.Candidate', votes=9, wins=6, category=cat1, is_enabled=True) # .6667
        
        mixer.blend('notorhot.Candidate', votes=18, wins=17, category=cat2) 
        mixer.blend('notorhot.Candidate', votes=15, wins=14, category=cat2) 
        mixer.blend('notorhot.Candidate', votes=12, wins=11, category=cat2) 
        mixer.blend('notorhot.Candidate', votes=9, wins=8, category=cat2) 
        
        mixer.blend('notorhot.Candidate', votes=18, wins=17, category=cat1, is_enabled=False) 
        mixer.blend('notorhot.Candidate', votes=15, wins=14, category=cat1, is_enabled=False) 
        mixer.blend('notorhot.Candidate', votes=12, wins=11, category=cat1, is_enabled=False) 
        mixer.blend('notorhot.Candidate', votes=9, wins=8, category=cat1, is_enabled=False) 
        
        in_order = Candidate.enabled.for_category(cat1).order_by_wins()
        # get win count for ordered candidates = should be 6, 7, 8, 9
        wins = [c.wins for c in in_order]
        self.assertEqual(wins, [6, 7, 8, 9])
        self.assertEqual(in_order.count(), 4)
        
    def test_incrementing(self):
        cand = mixer.blend('notorhot.Candidate', challenges=1, votes=1, wins=1)

        cand.increment_challenges()        
        self.assertEqual(cand.challenges, 2)
        
        cand.increment_votes(True)
        self.assertEqual(cand.votes, 2)
        self.assertEqual(cand.wins, 2)
        
        cand.increment_votes(False)
        self.assertEqual(cand.votes, 3)
        self.assertEqual(cand.wins, 2)
        
    def test_win_percentage(self):
        cand = mixer.blend('notorhot.Candidate', votes=10, wins=5)
        
        self.assertEqual(cand.win_percentage, 50.0)
            
    
class NotorHotCompetitionTestCase(TestCase):
    pass