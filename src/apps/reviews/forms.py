from django import forms
from django.forms import Textarea
from django.utils.translation import ugettext as _
from apps.reviews.models import Review

__author__ = 'daniel'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text']
        widgets = {
            'text': Textarea(
                attrs={
                    'cols': None,
                    'rows': None,
                    'class': 'form-control',
                    'placeholder': _('Write a review!')
                }
            ),
        }
