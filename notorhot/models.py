from django.db import models
from django.utils.translation import ugettext as _, ugettext_lazy as _l
from django.core.exceptions import ValidationError

from sorl.thumbnail import ImageField
from model_utils import Choices


class EnabledCandidateManager(models.Manager):
    def get_queryset(self):
        return super(EnabledCandidateManager, self).get_queryset().filter(
            is_enabled=True)
    

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    pic = ImageField(upload_to='candidates')
    is_enabled = models.BooleanField(default=True)
    
    challenges = models.PositiveIntegerField(default=0, blank=True, 
        help_text=_l(u"Number of times this candidate has been presented to users"))
    votes = models.PositiveIntegerField(default=0, blank=True, 
        help_text=_l(u"Number of times users have submitted votes in comparison "
            u"that included this candidate."))
    wins = models.PositiveIntegerField(default=0, blank=True, 
        help_text=_l(u"Number of competitions this candidate has won"))
        
    added = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    enabled = EnabledCandidateManager()

    def __unicode__(self):
        return self.name
    
    
class CompetitionManager(models.Manager):
    def generate_from_candidates(self, left, right):
        return self.create(**{
            'left': left,
            'right': right,
        })

    def generate_from_queryset(self, queryset):
        # randomize queryset order, then select first two objects
        first_2 = queryset.order_by('?')[:2]
        
        # Not enough candidates available total
        if len(first_2) < 2:
            raise Candidate.DoesNotExist

        return self.generate_from_candidates(first_2[0], first_2[1])
        
    def generate(self):
        return self.generate_from_queryset(Candidate.enabled.all())


class VotableCompetitionManager(models.Manager):
    def get_queryset(self):
        return super(VotableCompetitionManager, self).get_queryset().filter(
            date_voted__isnull=True)
    


class Competition(models.Model):
    SIDES = Choices(
        (1, 'LEFT', _l(u"Left")),
        (2, 'RIGHT', _l(u"Right")),
    )

    date_presented = models.DateTimeField(auto_now_add=True)
    date_voted = models.DateTimeField(null=True, blank=True)
    
    left = models.ForeignKey(Candidate, related_name='comparisons_left', 
        help_text=_l(u"Candidate to present on the left-hand side of the comparison"))
    right = models.ForeignKey(Candidate, related_name='comparisons_right', 
        help_text=_l(u"Candidate to present on the right-hand side of the comparison"))
        
    winner = models.ForeignKey(Candidate, related_name='comparisons_won', 
        null=True, blank=True,
        help_text=_l(u"Candidate who won the competition"))
    
    winning_side = models.PositiveSmallIntegerField(null=True, blank=True, 
        choices=SIDES)
        
    objects = CompetitionManager()
    votable = VotableCompetitionManager()
        
    def __unicode__(self):
        return "%s vs. %s" % (self.left, self.right)
        
    def clean(self):
        if self.winner and self.winner.id not in (self.left.id, self.right.id):
            raise ValidationError(_(u"Winner must be one of the candidates "
                u"offered on left or right."))
