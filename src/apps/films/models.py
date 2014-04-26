# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.db import models


class Person(models.Model):
    """
    Person model.
    """
    person_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=120)

    def __unicode__(self):
        return self.name


class Genre(models.Model):
    """
    film genre model.
    """
    genre_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return self.name


class Film(models.Model):
    """
    film model.
    """
    film_id = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=250)
    year = models.PositiveSmallIntegerField(null=True)
    runtime = models.PositiveSmallIntegerField(null=True)
    rating = models.CharField(max_length=24, null=True)
    released = models.DateField(null=True)
    plot = models.TextField(null=True)
    fullplot = models.TextField(null=True)
    poster = models.URLField(null=True)
    n_votes = models.PositiveIntegerField(default=0)
    sum_votes = models.FloatField(default=0)

    director = models.ManyToManyField(Person, related_name="director")
    writer = models.ManyToManyField(Person, related_name="writer")
    cast = models.ManyToManyField(Person, related_name="cast")
    genre = models.ManyToManyField(Genre)

    def __unicode__(self):
        return self.title

    @property
    def score(self):
        return self.sum_votes / self.n_votes if self.n_votes != 0 else None

    def rate(self, user, score):
        """
        Updates film model with a new rating.
        :param user: user
        :type user: apps.users.models.MyUser
        :param score: score
        :type score: float
        :return: nothing
        :rtype: None
        """
        results = user.get_rate_for_films([self])
        unused_film, old_score = results[0]

        user.rate(self, score)

        if old_score:
            self.sum_votes -= old_score
        else:
            self.n_votes += 1
        self.sum_votes += score
        self.save()


