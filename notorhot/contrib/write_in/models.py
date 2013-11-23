import datetime

from django.db import models
from django.utils.translation import ugettext as _, ugettext_lazy as _l

from model_utils import Choices

from notorhot.contrib.write_in.utils import AbstractFieldTracker

submission_tracker = AbstractFieldTracker(fields=['status',])

class WriteInBase(models.Model):
    STATUS = Choices(
        (1, 'SUBMITTED', _l(u"Submitted")),
        (2, 'ACCEPTED', _l(u"Accepted")),
        (3, 'REJECTED', _l(u"Rejected")),
    )

    candidate_name = models.CharField(max_length=100)
    # NOTE: we won't restrict to public categories in case we're gathering for
    # a new upcoming category.
    category = models.ForeignKey('notorhot.CandidateCategory')
    status = models.PositiveIntegerField(blank=True, choices=STATUS,
        default=STATUS.SUBMITTED)
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_processed = models.DateTimeField(null=True, blank=True)
    
    def __init__(self, *args, **kwargs):
        submission_tracker.finalize_class(self.__class__, 'submission_tracker')
        super(WriteInBase, self).__init__(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        
        # new status
        prev_status = self.submission_tracker.previous('status') 
        if prev_status == self.STATUS.SUBMITTED and \
                self.status != self.STATUS.SUBMITTED:
            self.date_processed = datetime.datetime.now()
            # @TODO: send signal!

        created = True
        if not self.pk:
            created = False
            if self.status is None:
                self.status = self.STATUS.SUBMITTED
            
        super(WriteInBase, self).save(*args, **kwargs)
        
        if created:
            # @TODO: send created signal
            pass

    class Meta:
        abstract = True
        

class SubmitterInfoMixin(models.Model):
    submitter_name = models.CharField(max_length=100)
    submitter_email = models.EmailField()
    
    def __unicode__(self):
        return _l(u"%s submitted by %s") % (self.candidate_name, self.submitter_name)

    class Meta:
        abstract = True


class DefaultWriteIn(SubmitterInfoMixin, WriteInBase):
    class Meta:
        verbose_name = _l(u"Write-in Candidate")