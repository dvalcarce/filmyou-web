# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.db import models
from django.contrib.auth.models import User

from libs.cassandra import CassandraAdapter


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
    Movie genre model.
    """
    genre_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return self.name


class Movie(models.Model):
    """
    Movie model.
    """
    movie_id = models.PositiveIntegerField(primary_key=True)
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
        Updates movie model with a new rating.
        :param user: user
        :type user: MyUser
        :param score: score
        :type score: float
        :return: nothing
        :rtype: None
        """
        results = user.get_rate_for_movies([self])
        unused_movie, old_score = results[0]

        user.rate(self, score)

        if old_score:
            self.sum_votes -= old_score
        else:
            self.n_votes += 1
        self.sum_votes += score
        self.save()


class MyUser(User):
    class Meta:
        proxy = True

    def get_rate_for_movies(self, movies):
        """
        Returns the rates for the given movies in a 'zipped way':
            [(movie1, rate1), (movie2, rate2)...]
        """
        rates = []
        for movie in movies:
            query = "SELECT movie, score FROM ratings WHERE user = %(user)s AND movie = %(movie)s"
            parameters = {
                'user': self.id,
                'movie': int(movie.movie_id),
            }
            with CassandraAdapter() as db:
                results = db.execute(query, parameters)
            if results:
                rates.append(results[0][1])
            else:
                rates.append(None)

        # Commentend until bug CASSANDRA-6137 is resolved

        # query = "SELECT movie, score FROM ratings WHERE user = :user AND movie IN :movies"
        # parameters = {
        #     'user': self.id,
        #     'movies': tuple(sorted(tuple(int(movie.movie_id) for movie in movies))),
        # }
        # with CassandraAdapter() as db:
        #     results = dict(db.execute(query, parameters))

        # rates = []
        # for movie in movies:
        #     if movie.movie_id in results:
        #         rates.append(results[movie.movie_id])
        #     else:
        #         rates.append(None)

        return zip(movies, rates)

    def get_ratings(self, last=None, n_results=10):
        """
        Returns a list of rated movies by self:
            [(movie1, rate1), (movie2, rate2)...]
        """
        parameters = {
            'user': self.id,
            'limit': n_results
        }
        if last:
            query = "SELECT movie, score " \
                    "FROM ratings " \
                    "WHERE user = %(user)s AND movie > %(last)s " \
                    "LIMIT %(limit)s"
            parameters['last'] = last
        else:
            query = "SELECT movie, score " \
                    "FROM ratings " \
                    "WHERE user = %(user)s " \
                    "LIMIT %(limit)s"

        with CassandraAdapter() as db:
            result = db.execute(query, parameters)

        return [
            (Movie.objects.get(movie_id=movie), score) for (movie, score) in
            result
        ]

    def get_recommendations(self, last=None, n_results=10):
        """
        Get recommendations for self from Cassandra DB:
            [(movie1, predicted_rate1), (movie2, predicted_rate2)...]
        """
        parameters = {
            'user': self.id,
            'limit': n_results
        }

        if last:
            query = "SELECT movie, score " \
                    "FROM recommendations " \
                    "WHERE user = %(user)s AND movie > " \
                    "%(last)s LIMIT %(limit)s"
            parameters['last'] = last
        else:
            query = "SELECT movie, score " \
                    "FROM recommendations " \
                    "WHERE user = %(user)s " \
                    "LIMIT %(limit)s"

        with CassandraAdapter() as db:
            result = db.execute(query, parameters)

        return [
            (Movie.objects.get(movie_id=movie), score) for (movie, score) in
            result
        ]

    def rate(self, movie, score):
        """
        Inserts new rating in Cassandra DB.
        """
        query = "INSERT INTO ratings (user, movie, score) " \
                "VALUES (:user, :movie, :score)"
        parameters = {
            'user': self.id,
            'movie': movie.movie_id,
            'score': float(score)
        }

        with CassandraAdapter() as db:
            db.execute(query, parameters)
