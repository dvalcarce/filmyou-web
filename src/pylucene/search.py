#!/usr/bin/env python

INDEX_DIR = "pylucene/Movies.index"

import os, lucene, functools

from datetime import datetime

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher, ScoreDoc
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

from filmyou.models import Movie


class MovieReader(object):
    """
    This is an utility class designed for querying Lucene indexes about movies.
    """

    def __init__(self):
        """
        Instantiates a MovieReader object capable of reading Lucene indexes contents.
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

        f = functools.partial(LuceneMovie.init_args, self)
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

        f = functools.partial(LuceneMovie.init_args, self)
        return map(f, scoreDocs)

    def get_fields(self, movie, field, numeric=False):
        """
        Returns a list with the contents of the fields with the given name
        in the movie.
        If numeric is set to True, a numeric representation of the data is
        returned instead of a string one.
        """
        content = movie.getFields(field)
        if numeric:
            f = lambda x: x.numericValue()
        else:
            f = lambda x: x.stringValue() if x.stringValue() != "N/A" else None
        return map(f, content)


class LuceneMovie(object):
    """
    This class encapsulates a movie stored in a Lucene index
    """

    @classmethod
    def init_args(self, reader, x):
        """
        This method instantiates a valid LuceneMovie object given a
        MovieReader and a ScoreDoc.
        """
        return LuceneMovie(reader, x.doc, x.score, reader.searcher.doc(x.doc))

    def __init__(self, reader, doc_id, score, movie):
        """
        LuceneMovie constructor.
        """
        self.doc_id = doc_id
        self.score = score
        self.movie_id = reader.get_fields(movie, "id")[0]
        self.title = reader.get_fields(movie, "title")[0]
        self.year = reader.get_fields(movie, "year", numeric=True)[0]
        self.genres = reader.get_fields(movie, "genre")
        self.runtime = reader.get_fields(movie, "runtime")[0]
        self.rating = reader.get_fields(movie, "rating")[0]
        self.directors = reader.get_fields(movie, "director")
        self.writers = reader.get_fields(movie, "writer")
        self.casts = reader.get_fields(movie, "cast")

        ts = reader.get_fields(movie, "released", numeric=True)[0].longValue()
        self.released = datetime.fromtimestamp(ts) if ts != -2**63 else None

        self.plot = reader.get_fields(movie, "plot")[0]
        self.fullplot = reader.get_fields(movie, "fullplot")[0]
        self.poster = reader.get_fields(movie, "poster")[0]

        movie = Movie.objects.get(movie_id=self.movie_id)
        self.n_votes = movie.n_votes
        self.sum_votes = movie.sum_votes

    def __unicode__(self):
        return u"{id}: '{title}'".format(id=self.movie_id, title=self.title)

    def __repr__(self):
        return self.__unicode__()


# Initialize Lucene
lucene.initVM()
base_dir = os.path.abspath(os.path.curdir)
index_file = os.path.join(base_dir, INDEX_DIR)
index = SimpleFSDirectory(File(index_file))
reader = DirectoryReader.open(index)
searcher = IndexSearcher(reader)
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
