import datetime

from django.test import TestCase
from django.core.exceptions import ValidationError

from notorhot._tests.factories import mixer
from notorhot._tests._utils import generate_leaderboard_data
from notorhot.models import CandidateCategory, Candidate, Competition

class NotorHotCategoryTestCase(TestCase):
    def test_category_publicity_manager(self):
        mixer.blend('notorhot.CandidateCategory', is_public=True)
        mixer.blend('notorhot.CandidateCategory', is_public=False)
        self.assertEqual(CandidateCategory.objects.count(), 2)
        self.assertEqual(CandidateCategory.public.count(), 1)

    def test_category_competition_generator(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        
        with self.assertRaises(Candidate.DoesNotExist):
            cat.generate_competition()
        
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
        
    def test_manager_and_queryset_chaining(self):
        cat1 = mixer.blend('notorhot.CandidateCategory')
        cat2 = mixer.blend('notorhot.CandidateCategory')
        
        (cand1, cand2, cand3, cand4) = generate_leaderboard_data(cat1, cat2)
        
        in_order = Candidate.enabled.for_category(cat1).order_by_wins()
        # get win count for ordered candidates = should be 6, 7, 8, 9
        wins = [c.wins for c in in_order]
        self.assertEqual(wins, [6, 7, 8, 9])
        self.assertEqual(list(in_order), [cand4, cand3, cand2, cand1])
        
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
        
        cand = mixer.blend('notorhot.Candidate', votes=0, wins=0)
        self.assertEqual(cand.win_percentage, 'No votes')
            
    
class NotorHotCompetitionTestCase(TestCase):
    def test_votable_manager(self):
        mixer.cycle(3).blend('notorhot.Competition', date_voted=None)
        mixer.cycle(2).blend('notorhot.Competition', 
            date_voted=datetime.datetime.now())

        self.assertEqual(Competition.votable.count(), 3)
        
    def test_generating_manager(self):
        with self.assertRaises(Candidate.DoesNotExist):
            comp = Competition.objects.generate_from_queryset(
                Candidate.objects.all()) 
                
        self.assertEqual(Competition.objects.count(), 0)

        cands = []
        for i in range(6):
            cands.append(mixer.blend('notorhot.Candidate', name='Cand%d' % i, 
                votes=i, enabled=True))
            
        comp = Competition.objects.generate_from_candidates(cands[0], cands[1])
        self.assertEqual(Competition.objects.count(), 1)
        self.assertIsNone(comp.date_voted)
        self.assertEqual(comp.left, cands[0])
        self.assertEqual(comp.right, cands[1])
        
        unpopular = Candidate.objects.filter(votes__lt=3)
        
        for i in range(100):
            comp = Competition.objects.generate_from_queryset(unpopular)        
            self.assertEqual(Competition.objects.count(), i + 2)
            self.assertTrue(comp.left in unpopular)
            self.assertTrue(comp.right in unpopular)
            
        Competition.objects.delete()

        self.assertEqual(Competition.objects.count(), 0)
        
    
    def test_clean(self):
        cat1 = mixer.blend('notorhot.CandidateCategory')
        cat2 = mixer.blend('notorhot.CandidateCategory')
        cands = mixer.cycle(3).blend('notorhot.Candidate', category=cat1, 
            is_enabled=True)
        cand_cat2 = mixer.blend('notorhot.Candidate', category=cat2, 
            is_enabled=True)
        
        try:
            comp = Competition(**{
                'left': cands[0],
                'right': cands[1],
            })
            comp.clean()
        except ValidationError:
            self.fail(u"Competition with no winner or category set should clean "
                u"without trouble.")

        try:
            comp = Competition(**{
                'left': cands[0],
                'right': cands[1],
                'winner': cands[0],
                'category': cat1,
            })
            comp.clean()
        except ValidationError:
            self.fail(u"Competition with winner and category matching candidates "
                u"shoudl clean without trouble")

        # winner in same category but difft competition
        with self.assertRaises(ValidationError):
            comp = Competition(**{
                'left': cands[0],
                'right': cands[1],
                'winner': cands[2],
            })
            comp.clean()

        # category doesn't match candidates
        with self.assertRaises(ValidationError):
            comp = Competition(**{
                'left': cands[0],
                'right': cands[1],
                'category': cat2,
            })
            comp.clean()

        # candidates from different categories
        with self.assertRaises(ValidationError):
            comp = Competition(**{
                'left': cands[0],
                'right': cand_cat2,
            })
            comp.clean()
            
        
    def test_save(self):
        self.assertEqual(Competition.objects.count(), 0)
        
        cat1 = mixer.blend('notorhot.CandidateCategory')
        cat2 = mixer.blend('notorhot.CandidateCategory')
        cands = mixer.cycle(3).blend('notorhot.Candidate', category=cat1, 
            is_enabled=True, challenges=0)
                
        comp = Competition(**{
            'left': cands[0],
            'right': cands[1],
        })
        
        comp.save()
        
        self.assertEqual(Competition.objects.count(), 1)
        self.assertEqual(cands[0].challenges, 1)
        self.assertEqual(cands[1].challenges, 1)
        self.assertEqual(comp.category, cat1)
        self.assertIsNone(comp.winner)
        self.assertIsNone(comp.winning_side)
        self.assertIsNone(comp.date_voted)
        self.assertIsNotNone(comp.date_presented)    
        
        # make sure saving again doesn't set any new values
        comp.save()
        
        self.assertEqual(Competition.objects.count(), 1)
        self.assertEqual(cands[0].challenges, 1)
        self.assertEqual(cands[1].challenges, 1)
        self.assertEqual(comp.category, cat1)
        self.assertIsNone(comp.winner)
        self.assertIsNone(comp.winning_side)
        self.assertIsNone(comp.date_voted)
        self.assertIsNotNone(comp.date_presented)    
        
        
        
    def test_record_vote(self):
        cands = mixer.cycle(2).blend('notorhot.Candidate', is_enabled=True, 
            challenges=0, votes=0, wins=0)
            
        comp = Competition.objects.generate_from_candidates(cands[0], cands[1])
        
        self.assertEqual(cands[0].challenges, 1)
        self.assertEqual(cands[0].votes, 0)
        self.assertEqual(cands[0].wins, 0)
        self.assertIsNone(comp.winner)
        self.assertIsNone(comp.winning_side)
        self.assertIsNone(comp.date_voted)
        
        comp.record_vote(Competition.SIDES.RIGHT)

        self.assertEqual(cands[0].challenges, 1)
        self.assertEqual(cands[0].votes, 1)
        self.assertEqual(cands[0].wins, 0)
        self.assertEqual(cands[1].votes, 1)
        self.assertEqual(cands[1].wins, 1)
        self.assertEqual(comp.winner, cands[1])
        self.assertEqual(comp.winning_side, Competition.SIDES.RIGHT)
        self.assertIsNotNone(comp.date_voted)
        
        # shouldn't be able to record a vote on a competition that's already
        # been voted on
        with self.assertRaises(Competition.AlreadyVoted):
            comp.record_vote(Competition.SIDES.RIGHT)
