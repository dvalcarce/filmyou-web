# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os

import logging

import lucene
from django.conf import settings

from apps.films.models import Film
from apps.utils.db import retrieve_in_order_from_db
from java.io import File

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader, Term
from org.apache.lucene.search import IndexSearcher, ScoreDoc
from org.apache.lucene.search import BooleanQuery, BooleanClause, NumericRangeQuery, TermQuery
from org.apache.lucene.search.spans import SpanNearQuery, SpanTermQuery
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.queryparser.classic import MultiFieldQueryParser
from org.apache.lucene.queries import CustomScoreQuery
from org.apache.lucene.queries.mlt import MoreLikeThis
from org.apache.lucene.queries.function import FunctionQuery
from org.apache.lucene.queries.function.valuesource import LinearFloatFunction, PowFloatFunction, \
    DoubleConstValueSource, ScaleFloatFunction, IntFieldSource


class FilmSearcher(object):
    """
     This is an utility class designed for querying Lucene indexes.
     """

    def __enter__(self):
        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()
        self.reader = reader
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

    def _create_query(self, fields):
        """
        Build query with Term, Phrase and Fuzzy clauses.
        :param fields: dictionary of (field, text) tuples
        :return: query
        """
        query = BooleanQuery()
        for (field, text) in fields:
            if field.startswith("year"):
                start, end = text.split(",")
                numeric_query = NumericRangeQuery.newIntRange(
                    'year', int(start), int(end), True, True)
                query.add(BooleanClause(numeric_query, BooleanClause.Occur.MUST))
            if field == 'title':
                spans = []
                for word in text.lower().split():
                    spans.append(SpanTermQuery(Term(field, word)))
                query.add(BooleanClause(SpanNearQuery(spans, 2, True), BooleanClause.Occur.SHOULD))

        field_names, field_texts = zip(*fields)
        flags = [BooleanClause.Occur.MUST] * len(field_names)

        query_parser_query = MultiFieldQueryParser.parse(
            Version.LUCENE_CURRENT,
            field_texts,
            field_names,
            flags,
            StandardAnalyzer(Version.LUCENE_CURRENT))
        query.add(BooleanClause(query_parser_query, BooleanClause.Occur.MUST))

        fuzzify = lambda s: (s + " ").replace(" ", "~1 ")
        fuzzy_field_texts = map(fuzzify, field_texts)

        fuzzy_query_parser_query = MultiFieldQueryParser.parse(
            Version.LUCENE_CURRENT,
            fuzzy_field_texts,
            field_names,
            flags,
            StandardAnalyzer(Version.LUCENE_CURRENT))
        query.add(BooleanClause(fuzzy_query_parser_query, BooleanClause.Occur.MUST))

        boostQuery = FunctionQuery(
            LinearFloatFunction(
                PowFloatFunction(
                    DoubleConstValueSource(0.0001),
                    ScaleFloatFunction(IntFieldSource("imdb_votes_boost"), 0.0, 1.0)
                ), -1.0, 1.0))
        query = CustomScoreQuery(query, boostQuery)

        return query

    def query(self, fields, count=12):
        """
        Searches for a list of films that matches the given query.
        :param fields: a list of tuples (field_name, field_text)
        :param count: number of results
        :return: a list of films that match the query
        """
        if not fields:
            return []

        query = self._create_query(fields)

        score_docs = self.searcher.search(query, count).scoreDocs

        return self._retrieve_in_order(score_docs)

    def query_after(self, fields, last_id, last_score, count=12):
        """
        Searches for a list of films that matches the given query after the given last document.
        :param fields: a list of tuples (field_name, field_text)
        :param last_id: id of the last retrieved film
        :param last_score: score of the last retrieved film
        :param count: number of results
        :return: a list of films that match the query
        """
        if not fields:
            return []

        query = self._create_query(fields)
        last_doc = ScoreDoc(last_id, last_score)

        score_docs = self.searcher.searchAfter(last_doc, query, count).scoreDocs

        return self._retrieve_in_order(score_docs)

    def more_like_this(self, film, count=4):
        """
        Use query by document techniques to find related documents
        :param film: film
        :param count: number of results
        :return: a list of related films
        """
        # Retrieve doc id of the given film
        film_query = TermQuery(Term('id', str(film.film_id)))
        results = self.searcher.search(film_query, 1)
        if results.totalHits != 1:
            return []

        # Use MoreLikeThis query by document technology
        mlt = MoreLikeThis(reader)
        mlt.setFieldNames(["title", "director", "writer", "genre", "cast", "fullplot"])
        mlt.setMinTermFreq(0)
        mlt.setMinDocFreq(0)
        mlt.setAnalyzer(self.analyzer)
        mlt_query = mlt.like(results.scoreDocs[0].doc)

        # Filter the original film
        filtered_query = BooleanQuery()
        filtered_query.add(mlt_query, BooleanClause.Occur.MUST)
        filtered_query.add(film_query, BooleanClause.Occur.MUST_NOT)
        score_docs = self.searcher.search(filtered_query, count).scoreDocs

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
except lucene.JavaError as e:
    logger.error('Lucene not loaded')
