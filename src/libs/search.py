# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import functools
from datetime import datetime

from django.conf import settings
import lucene

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher, ScoreDoc
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from apps.films.models import Film


class filmReader(object):
    """
    This is an utility class designed for querying Lucene indexes about films.
    """

    def __init__(self):
        """
        Instantiates a filmReader object capable of reading Lucene indexes contents.
        :return: self
        :rtype: filmReader
        """
        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()
        self.searcher = searcher
        self.analyzer = analyzer


    def query(self, field, content, n_results=10, score=False):
        """
        Returns a list of the documents that match the query.
        """
        query = QueryParser(Version.LUCENE_CURRENT, field, self.analyzer).parse(content)
        topDocs = self.searcher.search(query, n_results)
        scoreDocs = topDocs.scoreDocs

        f = functools.partial(Lucenefilm.init_args, self)
        return map(f, scoreDocs)

    def search_after(self, field, content, last_id, last_score, n_results=10):
        """
        Returns a list of the documents that match the query.
        """
        # Build ScoreDoc from doc_id and score
        after = ScoreDoc(int(last_id), float(last_score))

        query = QueryParser(Version.LUCENE_CURRENT, field, self.analyzer).parse(content)
        topDocs = self.searcher.searchAfter(after, query, n_results)
        scoreDocs = topDocs.scoreDocs

        f = functools.partial(Lucenefilm.init_args, self)
        return map(f, scoreDocs)

    def get_fields(self, film, field, numeric=False):
        """
        Returns a list with the contents of the fields with the given name
        in the film.
        If numeric is set to True, a numeric representation of the data is
        returned instead of a string one.
        """
        content = film.getFields(field)
        if numeric:
            f = lambda x: x.numericValue()
        else:
            f = lambda x: x.stringValue() if x.stringValue() != "N/A" else None
        return map(f, content)


class Lucenefilm(object):
    """
    This class encapsulates a film stored in a Lucene index
    """

    @classmethod
    def init_args(self, reader, x):
        """
        This method instantiates a valid Lucenefilm object given a
        filmReader and a ScoreDoc.
        """
        return Lucenefilm(reader, x.doc, x.score, reader.searcher.doc(x.doc))

    def __init__(self, reader, doc_id, score, film):
        """
        Lucenefilm constructor.
        """
        self.doc_id = doc_id
        self.doc_score = score
        self.film_id = reader.get_fields(film, "id")[0]
        self.title = reader.get_fields(film, "title")[0]
        self.year = reader.get_fields(film, "year", numeric=True)[0]
        self.genres = reader.get_fields(film, "genre")
        self.runtime = reader.get_fields(film, "runtime")[0]
        self.rating = reader.get_fields(film, "rating")[0]
        self.directors = reader.get_fields(film, "director")
        self.writers = reader.get_fields(film, "writer")
        self.casts = reader.get_fields(film, "cast")

        ts = reader.get_fields(film, "released", numeric=True)[0].longValue()
        self.released = datetime.fromtimestamp(ts) if ts != -2 ** 63 else None

        self.plot = reader.get_fields(film, "plot")[0]
        self.fullplot = reader.get_fields(film, "fullplot")[0]
        self.poster = reader.get_fields(film, "poster")[0]

        try:
            film = Film.objects.get(film_id=self.film_id)
        except Film.DoesNotExist:
            return
        self.n_votes = film.n_votes
        self.sum_votes = film.sum_votes
        self.score = self.sum_votes / self.n_votes if self.n_votes != 0 else None

    def __unicode__(self):
        return u"{id}: '{title}'".format(id=self.film_id, title=self.title)

    def __repr__(self):
        return self.__unicode__()


# Initialize Lucene
lucene.initVM()
base_dir = os.path.abspath(os.path.curdir)
index_file = os.path.join(base_dir, settings.LUCENE['PATH'])
index = SimpleFSDirectory(File(index_file))
reader = DirectoryReader.open(index)
searcher = IndexSearcher(reader)
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
