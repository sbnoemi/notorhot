from django.db import models
from django.utils.translation import ugettext as _, ugettext_lazy as _l
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from notorhot.fields import AutoDocumentableImageField

from autoslug import AutoSlugField
from model_utils import Choices
from model_utils.managers import PassThroughManager

import datetime


class PublicCategoryManager(models.Manager):
    """
    Manager for :class:`CandidateCategory` that returns only instances with 
    :attr:`~CandidateCategory.is_public` ``== True``
    """
    def get_queryset(self):
        return super(PublicCategoryManager, self).get_queryset().filter(
            is_public=True)


class CandidateCategory(models.Model):
    """
    Category of "things" ("Candidates") to compare.  :class:`Candidate`
    instances belonging to different 
    :class:`CandidateCategories <CandidateCategory>` instances should never be
    offered up against one another in the same :class:`Competition`.
    """
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
        """
        URL for leaderboard for this category
        """
        return reverse('notorhot_leaders', kwargs={ 'category_slug': self.slug, })
        
    def generate_competition(self):
        """
        :returns: a :class:`Competition` instance with two :class:`Candidate` 
            instances selected at random from this :class:`CandidateCategory`.
        :rtype: :class:`Competition`
        """
        return Competition.objects.generate_from_queryset(
            self.candidates.enabled())
            
    @property
    def num_candidates(self):
        """
        :returns: number of enabled :class:`Candidate` instances belonging to 
            this :class:`CandidateCategory`.
        :rtype: integer
        """
        return self.candidates.enabled().count()
        
    def num_voted_competitions(self):
        """
        :returns: number of :class`Competition` instances in this 
            :class:`CandidateCategory` that have received votes.
        :rtype: integer
        """
        return self.competitions.count() - self.competitions.votable().count()
    num_voted_competitions = property(num_voted_competitions, doc="Competitions voted in")    
    
    class Meta:
        ordering = ('name',)
    
    

class CandidateQuerySet(models.query.QuerySet):
    """
    :class:`QuerySet` that adds additional ordering and filtering shortcut 
        methods for :class:`Candidate` sets.
    """
    def order_by_wins(self):
        """
        :returns: :class:`Candidate` queryset sorted by calculated win 
            percentage (wins/votes).
        :rtype: :class:`QuerySet`
        """
        return self.extra(select={ 'win_pct': '1.0 * wins / votes', }).order_by(
            '-win_pct')
            
    def for_category(self, category):
        """
        :arg category: :class:`CandidateCategory` by which the queryset should be
            filtered
        :returns: queryset filtered to include only :class:`Candidate` 
            instances belonging to the specified category.
        :rtype: :class:`QuerySet`
        """
        return self.filter(category=category)
        
    def enabled(self):
        """
        :returns: :class:`Candidate` queryset filtered to include ony instances 
            with :attr:`~Candidate.is_enabled` ``== True``
        :rtype: :class:`QuerySet`
        """
        return self.filter(is_enabled=True)


CandidateManager = PassThroughManager.for_queryset_class(CandidateQuerySet)


class EnabledCandidateManager(CandidateManager):
    """
    Manager that returns only :class:`Candidate` instances having 
    :attr:`~Candidate.is_enabled` ``== True``
    """
    def get_queryset(self):
        return super(EnabledCandidateManager, self).get_queryset().enabled()
    

class Candidate(models.Model):
    """
    Option to be voted on.  For instance, if our site lets us vote for the 
    awesomest fruit, we might have a :class:`Candidate` instance for Apples 
    and one for Bananas.
    """
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True)
    pic = AutoDocumentableImageField(upload_to='candidates')
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
        """
        Increments :attr:`~Candidate.votes` field.  If ``won == True``, also 
        increments :attr:`~Candidate.wins` field.
        
        :arg boolean won: Whether or not this was the winning candidate in 
            the vote.
        """
        self.votes += 1
        if won:
            self.wins += 1
        self.save()
        
    @property
    def win_percentage(self):
        """
        Calculated win rate (:attr:`~Candidate.wins`/:attr:`~Candidate.votes`)
        """
        if self.votes == 0:
            return 'No votes'
            
        return 100 * float(self.wins)/float(self.votes)
        
    def get_absolute_url(self):
        return reverse('notorhot_candidate', kwargs={ 
            'slug': self.slug, 
            'category_slug': self.category.slug,
        })
    

class CompetitionQuerySet(models.query.QuerySet):
    """
    QuerySet that adds additional filtering shortcut methods for 
    :class:`Competition` instances.
    """
    def votable(self):
        return self.filter(date_voted__isnull=True)


CompetitionManager = PassThroughManager.for_queryset_class(CompetitionQuerySet)


class CompetitionGeneratingManager(CompetitionManager):
    """
    :class:`CompetitionManager` with additional methods to generate 
    :class:`Competition` instances with randomized or specified 
    :class:`Candidate` instances.
    """
    def generate_from_candidates(self, left, right):
        """
        :arg left: :class:`Candidate` instance for the left side of the vote 
            display
        :arg right: :class:`Candidate` instance for the right side of the vote 
            display
        :returns: a new (not yet voted on) :class:`Competition` instance with 
            the specified "left" and "right" :class:`Candidate` instances.
        :rtype: :class:`Competition`
        """
        return self.create(**{
            'left': left,
            'right': right,
        })

    def generate_from_queryset(self, queryset):
        """
        Selects two :class:`Candidate` instances at random from the specified
        queryset, and creates a new :class:`Competition` between them.
        
        :arg queryset: pool of :class:`Candidate` instances from which to select
        :type queryset: :class:`QuerySet`
        :returns: new :class:`Competition` between two :class:`Candidate` 
            instances selected at random from ``queryset``
        :rtype: :class:`Competition`
        
        .. warning::
            If passed a queryset containing :class:`Candidate` instances
            belonging to multiple :class:`Categories <CandidateCategory>`, 
            this method is liable to generate a :class:`Competition` between 
            :class:`Candidates <Candidate>` belonging to different categories, 
            which is technically in violation of our business constraints.  No 
            validation currently exists to prevent this case.            
        """
        # randomize queryset order, then select first two objects
        first_2 = queryset.order_by('?')[:2]
        
        # Not enough candidates available total
        if len(first_2) < 2:
            raise Candidate.DoesNotExist

        return self.generate_from_candidates(first_2[0], first_2[1])
        
    def generate(self):
        """
        Selects two :class:`Candidate` instances at random from the pool of all
        :class:`Candidate` instances, and creates a new :class:`Competition` 
        between them.
        
        :returns: new :class:`Competition` between two :class:`Candidate` 
            instances selected at random
        :rtype: :class:`Competition`
        
        .. warning::
            Use at your own risk.
            
            This method is liable tto generate a :class:`Competition` between 
            :class:`Candidates <Candidate>` belonging to different categories, 
            which is technically in violation of our business constraints.  No
            validation currently exists to prevent this case.
        """
        return self.generate_from_queryset(Candidate.enabled.all())


class VotableCompetitionManager(CompetitionManager):
    """
    Manager that returns only :class:`Competition` instances that have not yet
    been voted on (having :attr:`~Competition.date_voted` ``is None``)
    """
    def get_queryset(self):
        return super(VotableCompetitionManager, self).get_queryset().votable()
    


class Competition(models.Model):
    """
    A comparison between two :clas::`Candidate` instances ("left" and "right" 
    candidates) and -- if the user submits a vote -- the result of that vote.
    """
    
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
        """
        Validates that the winner is one of the :class:`Candidate` instances 
        belonging to this :class:`Competition` and that the competition's 
        category matches both of its candidates' categories.
        """
        if self.winner and self.winner.id not in (self.left.id, self.right.id):
            raise ValidationError(_(u"Winner must be one of the candidates "
                u"offered on left or right."))
                
        if ((self.left.category != self.right.category) or 
                (self.category and (self.left.category != self.category))):
            raise ValidationError(_(u"Both candidates for competition must "
                u"belong to same category as competition."))
                
    def save(self, *args, **kwargs):
        """
        Upon :class:`Competition` instance creation, increments challenge count
        on both its candidates; if category is blank, sets a value.
        """
        if not self.id:
            self.left.increment_challenges()
            self.right.increment_challenges()
            
        try:
            self.category
        except CandidateCategory.DoesNotExist:
            self.category = self.left.category
            
        super(Competition, self).save(*args, **kwargs)
            
                
    def record_vote(self, winner):
        """
        Records the winning candidate on the :class:`Competition`.  Also updates 
        statistics on both :class:`Candidate` records.
        """
        self.winning_side = winner
        
        if winner == self.SIDES.LEFT:
            self.winner = self.left
        elif winner == self.SIDES.RIGHT:
            self.winner = self.right
            
        self.left.increment_votes((winner == self.SIDES.LEFT))
        self.right.increment_votes((winner == self.SIDES.RIGHT))
            
        self.date_voted = datetime.datetime.now()
        
        self.save()
        
