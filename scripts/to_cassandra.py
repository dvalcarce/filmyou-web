#!/usr/bin/env python2

# -*- coding: utf-8 -*-

INDEX_DIR = "Films.index"

import sys
import os

import lucene

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import IndexReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version


# This script will prepare a CSV for Cassandra DB
if __name__ == '__main__':
    lucene.initVM()

    base_dir = os.path.abspath(os.path.curdir)
    index_file = os.path.join(base_dir, INDEX_DIR)
    store = SimpleFSDirectory(File(index_file))

    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

    reader = IndexReader.open(store)
    searcher = IndexSearcher(reader)

    query_parser = QueryParser(Version.LUCENE_CURRENT, "netflix_id", analyzer)

    with open(sys.argv[1], 'r') as ratings:
        for line in ratings:
            user_id, netflix_id, score = line.split(",")

            query = query_parser.parse(netflix_id)

            scoreDocs = searcher.search(query, 1).scoreDocs
            if scoreDocs:
                doc = searcher.doc(scoreDocs[0].doc)
                film_id = doc.getField("id").stringValue()
                print "{0},{1},{2}".format(user_id, film_id, score),
