from django.db import models
from django.contrib.auth.models import User

from filmyou.cassandra import CassandraAdapter


class Person(models.Model):
    person_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=120)

    def __unicode__(self):
        return self.name


class Genre(models.Model):
    genre_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return self.name


class Movie(models.Model):
    movie_id = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=250)
    year = models.PositiveSmallIntegerField(null=True)
    runtime = models.PositiveSmallIntegerField(null=True)
    rating = models.CharField(max_length=24, null=True)
    released = models.DateField(null=True)
    plot = models.TextField(null=True)
    fullplot = models.TextField(null=True)
    poster = models.URLField(null=True)

    director = models.ManyToManyField(Person, related_name="director")
    writer = models.ManyToManyField(Person, related_name="writer")
    cast = models.ManyToManyField(Person, related_name="cast")
    genre = models.ManyToManyField(Genre)

    def __unicode__(self):
        return self.title


class MyUser(User):
    class Meta:
        proxy = True

    def get_rate_for_movie(self, movie):
        query = "SELECT score FROM ratings WHERE user = :user AND movie = :movie"
        parameters = {
            'user': self.id,
            'movie': movie.movie_id,
        }

        with CassandraAdapter() as db:
            result = db.execute(query, parameters)

        return result

    def get_movies_rated(self):
        query = "SELECT movie, score FROM ratings WHERE user = :user"
        parameters = {
            'user': self.id,
        }

        with CassandraAdapter() as db:
            result = db.execute(query, parameters)

        return Movie.objects.filter(movie_id__in=result)

    def get_recommendations(self):
        query = "SELECT movie, score FROM recommendations WHERE user = :user"
        parameters = {
            'user': self.id,
        }

        with CassandraAdapter() as db:
            result = db.execute(query, parameters)

        return Movie.objects.filter(movie_id__in=result)
