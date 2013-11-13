from django.db import models
from django.utils.translation import ugettext as _, ugettext_lazy as _l
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from autoslug import AutoSlugField
from sorl.thumbnail import ImageField
from model_utils import Choices
from model_utils.managers import PassThroughManager

import datetime


class PublicCategoryManager(models.Manager):
    def get_queryset(self):
        return super(PublicCategoryManager, self).get_queryset().filter(
            is_public=True)


class CandidateCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True)
    is_public = models.BooleanField(default=True, help_text=_l(u"If false, "
        u"this category will not be listed, and competitions for this category "
        u"will not be available."))
    
    objects = models.Manager()
    public = PublicCategoryManager()
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('notorhot_competition', kwargs={ 'slug': self.slug, })
        
    def get_leaderboard_url(self):
        return reverse('notorhot_leaders', kwargs={ 'category_slug': self.slug, })
        
    def generate_competition(self):
        return Competition.objects.generate_from_queryset(
            self.candidates.enabled())
            
    @property
    def num_candidates(self):
        return self.candidates.enabled().count()
        
    def num_voted_competitions(self):
        return self.competitions.votable().count()
    num_voted_competitions = property(num_voted_competitions, doc="Competitions voted in")    
    #num_voted_competitions.short_description = 'Competitions Voted In'
    
    class Meta:
        ordering = ('name',)
    
    

class CandidateQuerySet(models.query.QuerySet):
    def order_by_wins(self):
        return self.extra(select={ 'win_pct': 'wins / votes', }).order_by(
            '-win_pct')
            
    def for_category(self, category):
        return self.filter(category=category)
        
    def enabled(self):
        return self.filter(is_enabled=True)


CandidateManager = PassThroughManager.for_queryset_class(CandidateQuerySet)


class EnabledCandidateManager(CandidateManager):
    def get_queryset(self):
        return super(EnabledCandidateManager, self).get_queryset().enabled()
    

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True)
    pic = ImageField(upload_to='candidates')
    is_enabled = models.BooleanField(default=True)
    
    category = models.ForeignKey(CandidateCategory, related_name='candidates')

    # These fields technically violate 3rd normal form, but are a lot less
    # expensive to update than to calculate.
    challenges = models.PositiveIntegerField(default=0, blank=True, 
        help_text=_l(u"Number of times this candidate has been presented to users"))
    votes = models.PositiveIntegerField(default=0, blank=True, 
        help_text=_l(u"Number of times users have submitted votes in comparison "
            u"that included this candidate."))
    wins = models.PositiveIntegerField(default=0, blank=True, 
        help_text=_l(u"Number of competitions this candidate has won"))
        
    added = models.DateTimeField(auto_now_add=True)

    objects = CandidateManager()
    enabled = EnabledCandidateManager()

    def __unicode__(self):
        return self.name
        
    def increment_challenges(self):
        self.challenges += 1
        self.save()
        
    def increment_votes(self, won):
        self.votes += 1
        if won:
            self.wins += 1
        self.save()
        
    @property
    def win_percentage(self):
        if self.votes == 0:
            return 'No votes'
            
        return 100 * float(self.wins)/float(self.votes)
        
    def get_absolute_url(self):
        return reverse('notorhot_candidate', kwargs={ 
            'slug': self.slug, 
            'category_slug': self.category.slug,
        })
    

class CompetitionQuerySet(models.query.QuerySet):
    def votable(self):
        return self.filter(date_voted__isnull=True)


CompetitionManager = PassThroughManager.for_queryset_class(CompetitionQuerySet)


class CompetitionGeneratingManager(CompetitionManager):
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


class VotableCompetitionManager(CompetitionManager):
    def get_queryset(self):
        return super(VotableCompetitionManager, self).get_queryset().votable()
    


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

    # denormalized for easier filtering
    category = models.ForeignKey(CandidateCategory, related_name='competitions')
        
    winner = models.ForeignKey(Candidate, related_name='comparisons_won', 
        null=True, blank=True,
        help_text=_l(u"Candidate who won the competition"))
    
    # denormalized for easier reporting
    winning_side = models.PositiveSmallIntegerField(null=True, blank=True, 
        choices=SIDES)
        
    objects = CompetitionGeneratingManager()
    votable = VotableCompetitionManager()
        
    def __unicode__(self):
        return "%s vs. %s" % (self.left, self.right)
        
    def clean(self):
        if self.winner and self.winner.id not in (self.left.id, self.right.id):
            raise ValidationError(_(u"Winner must be one of the candidates "
                u"offered on left or right."))
                
        if ((self.left.category != self.right.category) or 
                (self.category and (self.left.category != self.category))):
            raise ValidationError(_(u"Both candidates for competition must "
                u"belong to same category as competition."))
                
    def save(self, *args, **kwargs):
        if not self.id:
            self.left.increment_challenges()
            self.right.increment_challenges()
            
        try:
            self.category
        except CandidateCategory.DoesNotExist:
            self.category = self.left.category
            
        super(Competition, self).save(*args, **kwargs)
            
                
    def record_vote(self, winner):
        self.winning_side = winner
        
        if winner == self.SIDES.LEFT:
            self.winner = self.left
        elif winner == self.SIDES.RIGHT:
            self.winner = self.right
            
        self.left.increment_votes((winner == self.SIDES.LEFT))
        self.right.increment_votes((winner == self.SIDES.RIGHT))
            
        self.date_voted = datetime.datetime.now()
        
        self.save()
        
