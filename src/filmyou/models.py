from django.db import models


class Director(models.Model):
    name = models.CharField(max_length=80)

    def __unicode__(self):
        return self.name


class Writer(models.Model):
    name = models.CharField(max_length=80)

    def __unicode__(self):
        return self.name


class Cast(models.Model):
    name = models.CharField(max_length=80)

    def __unicode__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return self.name


class Movie(models.Model):
    movie_id = models.CharField(max_length=7, primary_key=True)
    title = models.CharField(max_length=60)
    year = models.PositiveSmallIntegerField()
    runtime = models.PositiveSmallIntegerField()
    rating = models.CharField(max_length=12)

    director = models.ManyToManyField(Director)
    writer = models.ManyToManyField(Writer)
    cast = models.ManyToManyField(Cast)
    genre = models.ManyToManyField(Genre)

    released = models.DateField()
    plot = models.TextField()
    fullplot = models.TextField()
    poster = models.URLField()

    def __unicode__(self):
        return self.title



