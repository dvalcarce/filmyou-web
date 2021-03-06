# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from userena.models import UserenaBaseProfile
from caching.base import CachingManager, CachingMixin

from apps.utils.db import retrieve_in_order_from_db
from apps.utils import poster
from libs.cassandra import CassandraConnection


class Person(CachingMixin, models.Model):
    """
    Person model.
    """
    person_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=150)

    objects = CachingManager()

    def __unicode__(self):
        return self.name


class Genre(CachingMixin, models.Model):
    """
    Film genre model.
    """
    genre_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    objects = CachingManager()

    def __unicode__(self):
        return self.name


class Country(CachingMixin, models.Model):
    """
    Film country model.
    """
    country_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    objects = CachingManager()

    def __unicode__(self):
        return self.name


class Language(CachingMixin, models.Model):
    """
    Film country model.
    """
    language_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    objects = CachingManager()

    def __unicode__(self):
        return self.name


class Film(CachingMixin, models.Model):
    """
    Film model
    """
    film_id = models.PositiveIntegerField(primary_key=True)
    imdb_id = models.PositiveIntegerField(unique=True)
    netflix_id = models.PositiveIntegerField(null=True, unique=True)
    title = models.CharField(max_length=300)
    year = models.PositiveSmallIntegerField(null=True)
    runtime = models.PositiveSmallIntegerField(null=True)
    rating = models.CharField(max_length=24, null=True)
    released = models.DateField(null=True)
    plot = models.TextField(null=True)
    metascore = models.PositiveIntegerField(null=True)
    imdb_rating = models.FloatField(null=True, default=0)
    imdb_votes = models.PositiveIntegerField(null=True, default=0)
    fullplot = models.TextField(null=True)
    poster = models.URLField(null=True)
    awards = models.PositiveIntegerField(null=True)
    updated = models.DateField(null=True)
    poster_file = models.ImageField(upload_to='posters', null=True)

    n_votes = models.PositiveIntegerField(default=0)
    sum_votes = models.FloatField(default=0)

    directors = models.ManyToManyField(Person, related_name="director")
    writers = models.ManyToManyField(Person, related_name="writer")
    casts = models.ManyToManyField(Person, related_name="cast")
    genres = models.ManyToManyField(Genre)
    countries = models.ManyToManyField(Country)
    languages = models.ManyToManyField(Language)

    objects = CachingManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('films:details', args=[self.film_id])

    def get_poster(self):
        if not self.poster_file:
            poster.retrieve(self)

        return self.poster_file

    @property
    def score(self):
        """
        Calculate film score:
            (1/2) imdb_votes                  sum_votes
            ---------------- * imdb_rating + -----------
              total_votes                    total_votes
        :return:
        """
        total_votes = self.imdb_votes + self.n_votes
        if total_votes:
            score = (self.imdb_votes * self.imdb_rating / 2.0 + self.sum_votes) / total_votes
        else:
            score = 0.0

        return score

    @property
    def similar_films(self):
        from libs.lucene import FilmSearcher

        with FilmSearcher() as searcher:
            return searcher.more_like_this(self)

    def set_preference(self, user):
        """
        Set the preference rated by the given user to the film.

        :param user: user
        """

        query = "SELECT score FROM ratings " \
                "WHERE user = %(user)s AND item = %(item)s"
        parameters = {
            'user': user.user.id,
            'item': self.film_id
        }

        # Retrieve ratings from Cassandra
        with CassandraConnection() as db:
            try:
                self.preference = db.execute(query, parameters)[0].score
            except IndexError:
                self.preference = None

    def rate(self, user, score):
        """
        Update film model with a new rating and remove recommendation if exists.

        :param user: user
        :param score: score
        """
        score = float(score)
        self.set_preference(user)

        insert_query = "INSERT INTO ratings (user, item, score) " \
                       "VALUES ( %(user)s, %(item)s, %(score)s )"
        select_query = "SELECT relevance FROM recommendations " \
                       "WHERE user = %(user)s AND item = %(item)s"

        parameters = {
            'user': user.user.id,
            'item': self.film_id,
            'score': float(score)
        }

        with CassandraConnection() as db:
            db.execute(insert_query, parameters)
            result = db.execute(select_query, parameters)
            if result:
                delete_query = "DELETE FROM recommendations " \
                               "WHERE user = %(user)s " \
                               "AND relevance = %(relevance)s " \
                               "AND item = %(item)s"
                parameters['relevance'] = result[0].relevance
                db.execute(delete_query, parameters)

        if self.preference:
            score -= self.preference
        else:
            self.n_votes += 1

        self.sum_votes += score
        self.save()


class MyUser(CachingMixin, UserenaBaseProfile):
    user = models.OneToOneField(User, unique=True, related_name='profile')

    objects = CachingManager()

    def get_preferences_for_films(self, films):
        """
        Get the ratings for the given films

        :param films: list of Film objects
        :return: list of films with preference attribute set
        """
        # query = "SELECT item, score FROM ratings WHERE user = %(user)s AND item IN %(films)s"
        query = "SELECT item, score FROM ratings WHERE user = %(user)s AND item IN (" \
                + ", ".join([str(film.film_id) for film in films]) + ")"
        parameters = {'user': self.user.id}

        # Retrieve ratings from Cassandra
        with CassandraConnection() as db:
            ratings = db.execute(query, parameters)

        # Set rating field
        ratings_dict = {item: score for (item, score) in ratings}
        for film in films:
            film.preference = ratings_dict.get(film.film_id, None)

        return films

    def get_rated_films(self, last=None, count=12):
        """
        Gets a list of rated films by self.

        :param last: id of the last film queried or None
        :param count: number of elements to be retrieved
        :return: list of films with preference attribute set
        """
        parameters = {
            'user': self.user.id,
            'limit': count
        }
        if last:
            query = "SELECT item, score " \
                    "FROM ratings " \
                    "WHERE user = %(user)s AND item > %(last)s " \
                    "LIMIT " \
                    "%(limit)s"
            parameters['last'] = last
        else:
            query = "SELECT item, score " \
                    "FROM ratings " \
                    "WHERE user = %(user)s " \
                    "LIMIT %(limit)s"

        # Retrieve ratings from Cassandra
        with CassandraConnection() as db:
            ratings = db.execute(query, parameters)

        # Retrieve films info from the RDBMS
        ids = [item for (item, score) in ratings]
        films = retrieve_in_order_from_db(Film, ids)

        # Set rating field
        ratings_dict = {item: score for (item, score) in ratings}
        for film in films:
            film.preference = ratings_dict.get(film.film_id, None)

        return films

    def get_recommendations(self, last=None, count=12):
        """
        Gets a list of recommended films for self.

        :param last: (relevance, item) tuple of the last film queried or None
        :param count: number of elements to be retrieved
        :return: list of films where relevance attribute is set
        """
        parameters = {
            'user': self.user.id,
            'limit': count
        }

        if last:
            query = "SELECT item, relevance " \
                    "FROM recommendations " \
                    "WHERE user = %(user)s " \
                    "AND relevance <= %(last_relevance)s " \
                    " LIMIT " \
                    "%(limit)s"

            parameters['last_relevance'] = last[0]
            parameters['last_item'] = last[1]

        else:
            query = "SELECT item, relevance " \
                    "FROM recommendations " \
                    "WHERE user = %(user)s " \
                    "LIMIT %(limit)s"

        # Retrieve recommendations from Cassandra
        with CassandraConnection() as db:
            recommendations = db.execute(query, parameters)

        # Retrieve films info from the RDBMS
        ids = [item for (item, score) in recommendations]
        films = retrieve_in_order_from_db(Film, ids)

        # Set relevance field
        recommendations_dict = {item: score for (item, score) in recommendations}
        for film in films:
            film.relevance = recommendations_dict.get(film.film_id, None)

        return films
