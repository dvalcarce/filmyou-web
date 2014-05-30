# -*- coding: utf-8 -*-

from __future__ import absolute_import

from os import path
import tempfile

from django.core.files import File

from django.conf import settings

import requests


def _set_from_url(film, url):
    print "Retrieving from", url
    request = requests.get(url, stream=True)
    if request.status_code != requests.codes.ok:
        raise KeyError(url)
    lf = tempfile.NamedTemporaryFile()
    for block in request.iter_content(1024 * 8):
        if not block:
            break
        lf.write(block)
    filename = path.join('posters', str(film.film_id) + ".jpg")
    film.poster_file.save(name=filename, content=File(lf))


def _get_trakt_url(imdb_id):
    summary_url = "http://api.trakt.tv/movie/summary.json/{apikey}/tt{imdb_id}".format(
        apikey=settings.TRAKT_APIKEY,
        imdb_id=imdb_id)
    summary = requests.get(summary_url)
    if summary.status_code != requests.codes.ok:
        raise KeyError(imdb_id)

    poster_url = summary.json()['images']['poster']

    return poster_url[:poster_url.rindex('.jpg')] + "-300.jpg"


def retrieve(film):
    print film
    if film.poster:
        try:
            return _set_from_url(film, film.poster)
        except KeyError:
            pass

    try:
        url = _get_trakt_url(film.imdb_id)
        _set_from_url(film, url)
        print "\tBut in Trakt"
    except KeyError:
        film.poster_file = path.join('posters', 'noposter.png')
        film.save()
