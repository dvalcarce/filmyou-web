from django.db import models


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

