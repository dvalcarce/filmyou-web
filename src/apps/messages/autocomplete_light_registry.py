# -*- coding: utf-8 -*-

import autocomplete_light

from django.contrib.auth.models import User


class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = User
    choices = User.objects.filter(profile__isnull=False)
    order_by = ['username']
    search_fields = ['username']
    attrs = {'placeholder': '', 'data-autocomplete-minimum-characters': 1}


autocomplete_light.register(UserAutocomplete)
