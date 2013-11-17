from django import forms
from django.utils.translation import ugettext as _

from notorhot.models import Competition, Candidate


class VoteForm(forms.Form):
    """
    Form for voting on a :class:`~notorhot.models.Competition`.
    
    Must be initialized with a ``competition`` keyword argument referring to the
    :class:`~notorhot.models.`Competition` model instance that is to be voted on::
    
       vote_form = VoteForm(request.POST, competition=some_competition)
       
    :param competition: The :class:`~notorhot.models.Competition` instance that
        is being voted on
    :type competition: :class:`~notorhot.models.Competition`
    """
    winner = forms.TypedChoiceField(widget=forms.HiddenInput, 
        choices=Competition.SIDES, coerce=int)

    def __init__(self, *args, **kwargs):
        self.competition = kwargs.pop('competition')
        super(VoteForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Throws a :exc:`~django.forms.ValidationError` if the competition has
        already been voted on.
        """
        if self.competition.date_voted is not None:
            raise forms.ValidationError(_(u"You've already voted on this competition!"))
            
        super(VoteForm, self).clean()
        return self.cleaned_data

    def save(self):
        """
        Records a vote on the competition.
        """
        winner = self.cleaned_data['winner']
        self.competition.record_vote(winner)