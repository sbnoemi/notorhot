import datetime
from mock import Mock, patch

from django.test import TestCase
from django.forms import ValidationError

from notorhot._tests.factories import mixer
from notorhot.models import CandidateCategory, Candidate, Competition
from notorhot.forms import VoteForm

class NotorHotVoteFormTestCase(TestCase):
    def test_clean(self):
        cands = mixer.cycle(3).blend('notorhot.Candidate', enabled=True)
        comp = mixer.blend('notorhot.Competition', left=cands[0], right=cands[1])
        
        # basic validation should work
        form = VoteForm({ 'winner': Competition.SIDES.LEFT, }, competition=comp)
        self.assertTrue(form.is_valid())
        
        # but if we have already voted, it shouldn't
        comp = mixer.blend('notorhot.Competition', left=cands[0], right=cands[1],
            date_voted=datetime.datetime.now())

        form = VoteForm({ 'winner': Competition.SIDES.LEFT, }, competition=comp)
        self.assertFalse(form.is_valid())
        
    def test_save(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        cands = mixer.cycle(2).blend('notorhot.Candidate', enabled=True, category=cat)
        comp = Competition.objects.generate_from_candidates(cands[0], cands[1])
        
        form = VoteForm({ 'winner': Competition.SIDES.LEFT, }, competition=comp)
        self.assertTrue(form.is_valid())
        
        with patch.object(comp, 'record_vote') as mock_record_vote:
            form.save()
            self.assertEqual(mock_record_vote.call_count, 1)
            self.assertEqual(mock_record_vote.call_args[0], 
                (Competition.SIDES.LEFT,))
    
