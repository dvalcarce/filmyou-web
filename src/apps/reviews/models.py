# -*- coding: utf-8 -*-

from django.conf import settings

from django.core.urlresolvers import reverse
from django.db import models
from caching.base import CachingManager, CachingMixin

from apps.films.models import Film
from apps.utils.models import TimeStampedModel


class Review(CachingMixin, TimeStampedModel):
    """
    Review Model
    """
    review_id = models.AutoField(primary_key=True)
    text = models.TextField()
    film = models.ForeignKey(Film, null=True)
    author = models.ForeignKey(settings.AUTH_PROFILE_MODULE, null=False)

    objects = CachingManager()

    def get_absolute_url(self):
        return reverse('films:details', args=[self.film.film_id])
