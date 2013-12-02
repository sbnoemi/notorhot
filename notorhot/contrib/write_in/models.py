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
    category = models.ForeignKey('notorhot.CandidateCategory', 
        related_name='%(class)s_write_ins')
    status = models.PositiveIntegerField(blank=True, choices=STATUS,
        default=STATUS.SUBMITTED)
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_processed = models.DateTimeField(null=True, blank=True)
    
    def __init__(self, *args, **kwargs):
        submission_tracker.finalize_class(self.__class__, 'submission_tracker')
        super(WriteInBase, self).__init__(*args, **kwargs)
    
    def _save_status(self, prev_status):
        if prev_status == self.STATUS.SUBMITTED and \
                self.status != self.STATUS.SUBMITTED:
            self.date_processed = datetime.datetime.now()
            # @TODO: send signal!
            
    def _handle_null_status(self, prev_status):
        # Prohibit clearing status by simply reverting it.
        if self.pk:
            self.status = prev_status
        # for new instances, initial status should be "Submitted"
        else:
            self.status = self.STATUS.SUBMITTED
    
    def save(self, *args, **kwargs):
        # deal with status changes
        prev_status = self.submission_tracker.previous('status') 
        self._save_status(prev_status)
        if self.status is None:
            self._handle_null_status(prev_status)

        created = (self.pk is None)
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