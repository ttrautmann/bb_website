from django import forms

from .models import Throw


class ThrowsForm(forms.ModelForm):
    class Meta:
        model = Throw
        fields = ('player', 'result', 'round')
