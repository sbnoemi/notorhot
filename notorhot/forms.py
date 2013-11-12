from django import forms
from django.utils.translation import ugettext as _

from notorhot.models import Competition, Candidate

import datetime


class VoteForm(forms.Form):
    winner = forms.TypedChoiceField(widget=forms.HiddenInput, 
        choices=Competition.SIDES, coerce=int)

    def __init__(self, *args, **kwargs):
        self.competition = kwargs.pop('competition')
        super(VoteForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.competition.date_voted is not None:
            raise forms.ValidationError(_(u"You've already voted on this competition!"))
            
        super(VoteForm, self).clean()
        return self.cleaned_data

    def save(self):
        winner = self.cleaned_data['winner']
        
        self.competition.winning_side = winner
        
        if winner == Competition.SIDES.LEFT:
            self.competition.winner = self.competition.left
        elif winner == Competition.SIDES.RIGHT:
            self.competition.winner = self.competition.right
            
        self.competition.date_voted = datetime.datetime.now()
        
        self.competition.save()