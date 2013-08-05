#!/usr/bin/env python

INDEX_DIR = "pylucene/Movies.index"

import sys, os, lucene

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version


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

    def query(self, field, content, n_results=1):
        """
        Returns a list of the documents that match the query.
        """
        query = QueryParser(Version.LUCENE_CURRENT, field, analyzer).parse(content)
        scoreDocs = searcher.search(query, n_results).scoreDocs

        return map(lambda x: searcher.doc(x.doc), scoreDocs)

    def get_fields(self, movie, field, numeric=False):
        """
        Returns a list with the contents of the fields with the given name
        in the movie.
        If numeric is set to True, a numeric representation of the data is
        returned instead of a string one.
        """
        content = movie.getFields(field)
        f = (lambda x: x.numericValue()) if numeric else (lambda x: x.stringValue())
        return map(f, content)


# Initialize Lucene
lucene.initVM()
base_dir = os.path.abspath(os.path.curdir)
index_file = os.path.join(base_dir, INDEX_DIR)
index = SimpleFSDirectory(File(index_file))
reader = DirectoryReader.open(index)
searcher = IndexSearcher(reader)
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
