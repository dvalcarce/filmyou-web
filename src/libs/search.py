# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import logging

from django.conf import settings
import lucene

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer

from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher, ScoreDoc
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.util import Version
from apps.films.models import Film
from apps.utils.db import retrieve_in_order_from_db


class FilmSearcher(object):
    """
     This is an utility class designed for querying Lucene indexes.
     """

    def __enter__(self):
        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()
        self.searcher = searcher
        self.analyzer = analyzer
        return self

    def __exit__(self, type, value, traceback):
        pass

    def _retrieve_in_order(self, score_docs):
        """
        Retrieve films from the RDBMS in order given score docs
        and set doc_id and doc_score for the last films
        :param score_docs: score docs
        :return: a list of films
        """
        # Get ids from score docs
        ids = [int(searcher.doc(hit.doc).get("id")) for hit in score_docs]

        films = retrieve_in_order_from_db(Film, ids)

        if films:
            films[-1].doc_id = score_docs[-1].doc
            films[-1].doc_score = score_docs[-1].score

        return films


    def query(self, field, text, count=10):
        """
        Searches for a list of films that matches the given query.
        :param field: searching field
        :param text: content of the field
        :param count: number of results
        :return: a list of films that match the query
        """
        query = QueryParser(Version.LUCENE_CURRENT, field, self.analyzer).parse(text)
        score_docs = self.searcher.search(query, count).scoreDocs

        return self._retrieve_in_order(score_docs)

    def query_after(self, field, text, last_id, last_score, count=10):
        """
        Searches for a list of films that matches the given query after the given last document.
        :param field: searching field
        :param text: content of the field
        :param last_id: id of the last retrieved film
        :param last_score: score of the last retrieved film
        :param count: number of results
        :return: a list of films that match the query
        """
        query = QueryParser(Version.LUCENE_CURRENT, field, self.analyzer).parse(text)
        last_doc = ScoreDoc(int(last_id), float(last_score))
        score_docs = self.searcher.searchAfter(last_doc, query, count).scoreDocs

        return self._retrieve_in_order(score_docs)


# Initialize Lucene
lucene.initVM()
logger = logging.getLogger(__name__)
logger.info('Initialising Lucene VM')
base_dir = os.path.abspath(os.path.curdir)
index_file = os.path.join(base_dir, settings.LUCENE['PATH'])
index = FSDirectory.open(File(index_file))
try:
    reader = DirectoryReader.open(index)
    searcher = IndexSearcher(reader)
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
except lucene.JavaError:
    logger.error('Lucene not loaded')
