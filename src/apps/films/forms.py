# -*- coding: utf-8 -*-

import autocomplete_light
from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _

from .models import Person, Country, Genre, Language, Film


class SearchForm(forms.Form):
    title = forms.ModelChoiceField(
        Film.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('FilmAutocomplete'),
        required=False,
        label=_('Title')
    )

    genre = forms.ModelChoiceField(
        Genre.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('GenreAutocomplete'),
        required=False,
        label=_('Genre')
    )

    language = forms.ModelChoiceField(
        Language.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('LanguageAutocomplete'),
        required=False,
        label=_('Language')
    )

    country = forms.ModelChoiceField(
        Country.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('CountryAutocomplete'),
        required=False,
        label=_('Country')
    )

    director = forms.ModelChoiceField(
        Person.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('PersonDirectorAutocomplete'),
        required=False,
        label=_('Director')
    )

    writer = forms.ModelChoiceField(
        Person.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('PersonWriterAutocomplete'),
        required=False,
        label=_('Writer')
    )

    cast = forms.ModelChoiceField(
        Person.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('PersonCastAutocomplete'),
        required=False,
        label=_('Cast')
    )

    year_start = forms.IntegerField(
        required=False,
        widget=forms.widgets.TextInput,
        validators=[RegexValidator("\d+")],
        label=_('Year start')
    )

    year_end = forms.IntegerField(
        required=False,
        widget=forms.widgets.TextInput,
        validators=[RegexValidator("\d+")],
        label=_('Year end')
    )
