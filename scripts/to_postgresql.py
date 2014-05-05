#!/usr/bin/env python2

# -*- coding: utf-8 -*-

INDEX_DIR = "Films.index"

import os
import time
import codecs

import lucene
import psycopg2

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexReader
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version


"""
This script scans OMDB collection and builds TSV files for PostgreSQL.
"""


class OutputSQL(object):
    def __init__(self, reader, store_dir):
        self.genres = {}
        self.people = {}
        self.languages = {}
        self.countries = {}
        self.store_dir = store_dir

        if not os.path.exists(self.store_dir):
            os.makedirs(store_dir)

        self.indexDocs(reader)

    def indexDocs(self, reader):
        with codecs.open(os.path.join(self.store_dir, "film.tsv"), 'w',
                         encoding='utf-8') as film_file, \
                codecs.open(os.path.join(self.store_dir, "person.tsv"), 'w',
                            encoding='utf-8') as person_file, \
                codecs.open(os.path.join(self.store_dir, "genre.tsv"), 'w',
                            encoding='utf-8') as genre_file, \
                codecs.open(os.path.join(self.store_dir, "genre_film.tsv"), 'w',
                            encoding='utf-8') as genre_film_file, \
                codecs.open(os.path.join(self.store_dir, "language.tsv"), 'w',
                            encoding='utf-8') as language_file, \
                codecs.open(os.path.join(self.store_dir, "language_film.tsv"), 'w',
                            encoding='utf-8') as language_film_file, \
                codecs.open(os.path.join(self.store_dir, "country.tsv"), 'w',
                            encoding='utf-8') as country_file, \
                codecs.open(os.path.join(self.store_dir, "country_film.tsv"), 'w',
                            encoding='utf-8') as country_film_file, \
                codecs.open(os.path.join(self.store_dir, "director.tsv"), 'w',
                            encoding='utf-8') as director_file, \
                codecs.open(os.path.join(self.store_dir, "writer.tsv"), 'w',
                            encoding='utf-8') as writer_file, \
                codecs.open(os.path.join(self.store_dir, "cast.tsv"), 'w',
                            encoding='utf-8') as cast_file:

            for i in xrange(reader.numDocs()):
                doc = reader.document(i)

                self.film_id = doc.getField("id").stringValue()
                imdb_id = doc.getField("imdb_id").stringValue()
                try:
                    netflix_id = doc.getField("netflix_id").stringValue()
                except AttributeError:
                    netflix_id = "NULL"

                title = self.parse_string(doc.getField("title").stringValue())
                year = self.parse_positive(doc.getField("year").numericValue().intValue())
                rating = self.parse_string(doc.getField("rating").stringValue())
                runtime = self.parse_positive(doc.getField("runtime").numericValue().intValue())
                released = self.parse_date(doc.getField("released").numericValue().longValue())

                metascore = self.parse_positive(doc.getField("metascore").numericValue().intValue())
                imdb_rating = self.parse_positive(
                    doc.getField("imdb_rating").numericValue().doubleValue())
                imdb_votes = self.parse_positive(
                    doc.getField("imdb_votes").numericValue().intValue())
                poster = self.parse_string(doc.getField("poster").stringValue())
                plot = self.parse_string(doc.getField("plot").stringValue())
                fullplot = self.parse_string(doc.getField("fullplot").stringValue())

                awards = self.parse_positive(doc.getField("awards").numericValue().intValue())
                updated = self.parse_date(doc.getField("updated").numericValue().longValue())

                self.parse_n_n(doc.getFields("genre"), self.genres, genre_file, genre_film_file)
                self.parse_n_n(doc.getFields("director"), self.people, person_file, director_file)
                self.parse_n_n(doc.getFields("writer"), self.people, person_file, writer_file)
                self.parse_n_n(doc.getFields("cast"), self.people, person_file, cast_file)
                self.parse_n_n(doc.getFields("language"), self.languages, language_file,
                               language_film_file)
                self.parse_n_n(doc.getFields("country"), self.countries, country_file,
                               country_film_file)

                film_file.write(u"{id}\t{imdb_id}\t{netflix_id}\t{title}\t{year}\t{rating}\t" \
                                "{runtime}\t{released}\t{metascore}\t{imdb_rating}\t{imdb_votes}\t" \
                                "{poster}\t{plot}\t{fullplot}\t{awards}\t{updated}\n".format(
                    id=self.film_id,
                    imdb_id=imdb_id,
                    netflix_id=netflix_id,
                    title=title,
                    year=year,
                    rating=rating,
                    runtime=runtime,
                    released=released,
                    metascore=metascore,
                    imdb_rating=imdb_rating,
                    imdb_votes=imdb_votes,
                    poster=poster,
                    plot=plot,
                    fullplot=fullplot,
                    awards=awards,
                    updated=updated)
                )

    def parse_string(self, text):
        if text == "" or text == "N/A":
            return "NULL"
        else:
            try:
                return unicode(text.replace("\t", " "))
            except Exception as e:
                print text
                raise e

    def parse_positive(self, number):
        if number < 0:
            return "NULL"
        else:
            return unicode(number)

    def parse_date(self, value):
        if value == -2 ** 63:
            return "NULL"

        t = time.gmtime(value)
        return u"{0}/{1}/{2}".format(t.tm_mday, t.tm_mon, t.tm_year)

    def parse_n_n(self, fields, entity, entity_f, relationship_file):
        if not fields:
            return
        for element in fields:
            element = element.stringValue()
            if not len(element):
                continue
            try:
                entity_id = entity[element]
            except KeyError:
                entity_id = len(entity) + 1
                entity[element] = entity_id
                entity_f.write(u"{id}\t{name}\n".format(id=entity_id, name=element))

            relationship_file.write(u"{m}\t{g}\n".format(m=self.film_id, g=entity_id))


if __name__ == '__main__':
    lucene.initVM()

    base_dir = os.path.abspath(os.path.curdir)
    index_file = os.path.join(base_dir, INDEX_DIR)
    store = SimpleFSDirectory(File(index_file))

    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

    reader = IndexReader.open(store)

    store_dir = os.path.join(base_dir, "sql")
    OutputSQL(reader, store_dir)
