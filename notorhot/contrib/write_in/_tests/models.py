import datetime
from mock import patch, Mock

from django.core.exceptions import ValidationError
from django.db import models, IntegrityError

from notorhot._tests.factories import mixer
from notorhot.models import CandidateCategory
from notorhot.contrib.write_in.models import DefaultWriteIn, WriteInBase, \
    SubmitterInfoMixin
from notorhot.contrib.write_in._tests._utils import ModelTestCase as TestCase

from model_utils.tracker import FieldInstanceTracker

class SimpleWriteIn(WriteInBase):
    class Meta:
        db_table = 'write_in_simple'
    

class SubmitterInfo(SubmitterInfoMixin, models.Model):
    candidate_name = models.CharField(max_length=100)
    class Meta:
        db_table = 'write_in_submitter'
    

class WriteInBaseTestCase(TestCase):
    apps = ('notorhot.contrib.write_in._tests',)

    def instantiate_tracker(self):
        # initialize submission_tracker -- because our model is abstract, 
        # we had to do an ugly workaround and initialize it only on first 
        # model instance init.
        mixer.blend(SimpleWriteIn)
    
    def test_init(self):
        if hasattr(SimpleWriteIn, 'submission_tracker'):
            self.fail(u"Submission tracker should not exist before __init__ is"
                u"called.")
        
        mixer.blend(SimpleWriteIn)
        self.assertIsNotNone(getattr(SimpleWriteIn, 'submission_tracker', None))
    
    def test_save(self):
        self.instantiate_tracker()
    
        write_in = mixer.blend(SimpleWriteIn, status=None,
            date_submitted=None)
        self.assertEqual(write_in.status, SimpleWriteIn.STATUS.SUBMITTED)
        self.assertIsNotNone(write_in.date_submitted)
        self.assertIsNone(write_in.date_processed)
            
        # check setting date_processed when status changes
        write_in.status = SimpleWriteIn.STATUS.ACCEPTED
        write_in.save()
        self.assertIsNotNone(write_in.date_processed)

        # well, technically, we should never be creating instances that are 
        # already accepted / rejected, but this is useful for testing a few 
        # other things
        write_in = mixer.blend(SimpleWriteIn, 
            status=SimpleWriteIn.STATUS.ACCEPTED)
        self.assertEqual(write_in.status, SimpleWriteIn.STATUS.ACCEPTED)
        self.assertIsNone(write_in.date_processed)
        
        write_in.status = None
        write_in.save()
        # preserve previous value on clearing pre-existing instance's status
        self.assertEqual(write_in.status, SimpleWriteIn.STATUS.ACCEPTED)
        self.assertIsNone(write_in.date_processed)
        
    def test_signals(self):
        pass
        

class SubmitterInfoMixinTestCase(TestCase):
    apps = ('notorhot.contrib.write_in._tests',)

    def test_unicode(self):
        submission = mixer.blend(SubmitterInfo, submitter_name='me', candidate_name='you')
        self.assertEqual(unicode(submission), u"you submitted by me")
        

class DefaultWriteInTestCase(TestCase):
    # Not sure we have anything to test on a unit test level right now, since we
    # should be able to safely assume that Django's abstract inheritance
    # works properly.
    pass