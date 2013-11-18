from django.test import TestCase

from notorhot._tests.factories import mixer
from notorhot.models import CandidateCategory, Candidate, Competition

class NotorHotModelTestCase(TestCase):
    def test_category_publicity_manager(self):
        mixer.blend('notorhot.CandidateCategory', is_public=True)
        mixer.blend('notorhot.CandidateCategory', is_public=False)
        self.assertEqual(CandidateCategory.objects.count(), 2)
        self.assertEqual(CandidateCategory.public.count(), 1)
