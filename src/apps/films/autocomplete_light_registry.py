# -*- coding: utf-8 -*-

import autocomplete_light

from .models import Person, Country, Genre, Film, Language


class DirectorAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = Person
    search_fields = ['name']
    order_by = ['name']
    choices = Person.objects.filter(director__isnull=False).distinct()
    attrs = {'placeholder': '', 'data-autocomplete-minimum-characters': 3}

    def choice_value(self, choice):
        return unicode(choice)


class WriterAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = Person
    search_fields = ['name']
    order_by = ['name']
    choices = Person.objects.filter(writer__isnull=False).distinct()
    attrs = {'placeholder': '', 'data-autocomplete-minimum-characters': 3}

    def choice_value(self, choice):
        return unicode(choice)


class CastAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = Person
    search_fields = ['name']
    order_by = ['name']
    choices = Person.objects.filter(cast__isnull=False).distinct()
    attrs = {'placeholder': '', 'data-autocomplete-minimum-characters': 3}

    def choice_value(self, choice):
        return unicode(choice)


class CountryAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = Country
    choices = Country.objects.all()
    search_fields = ['name']
    order_by = ['name']
    attrs = {'placeholder': '', 'data-autocomplete-minimum-characters': 3}

    def choice_value(self, choice):
        return unicode(choice)


class GenreAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = Genre
    choices = Genre.objects.all()
    search_fields = ['name']
    order_by = ['name']
    attrs = {'placeholder': '', 'data-autocomplete-minimum-characters': 3}

    def choice_value(self, choice):
        return unicode(choice)


class LanguageAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = Language
    choices = Language.objects.all()
    search_fields = ['name']
    order_by = ['name']
    attrs = {'placeholder': '', 'data-autocomplete-minimum-characters': 3}

    def choice_value(self, choice):
        return unicode(choice)


class FilmAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = Film
    choices = Film.objects.all()
    order_by = ['title']
    search_fields = ['title']
    attrs = {'placeholder': '', 'data-autocomplete-minimum-characters': 3}

    def choice_value(self, choice):
        return unicode(choice)


autocomplete_light.register(DirectorAutocomplete)
autocomplete_light.register(WriterAutocomplete)
autocomplete_light.register(CastAutocomplete)
autocomplete_light.register(CountryAutocomplete)
autocomplete_light.register(GenreAutocomplete)
autocomplete_light.register(LanguageAutocomplete)
autocomplete_light.register(FilmAutocomplete)

