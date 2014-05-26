# -*- coding: utf-8 -*-

import autocomplete_light

from django import forms

from .models import Person, Country, Genre, Language, Film


class SearchForm(forms.Form):
    title = forms.ModelChoiceField(
        Film.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('FilmAutocomplete'),
        required=False
    )

    genre = forms.ModelChoiceField(
        Genre.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('GenreAutocomplete'),
        required=False
    )

    language = forms.ModelChoiceField(
        Language.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('LanguageAutocomplete'),
        required=False
    )

    country = forms.ModelChoiceField(
        Country.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('CountryAutocomplete'),
        required=False
    )

    director = forms.ModelChoiceField(
        Person.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('PersonDirectorAutocomplete'),
        required=False
    )

    writer = forms.ModelChoiceField(
        Person.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('PersonWriterAutocomplete'),
        required=False
    )

    cast = forms.ModelChoiceField(
        Person.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('PersonCastAutocomplete'),
        required=False
    )

    year = forms.IntegerField(required=False)

    runtime = forms.IntegerField(required=False)
