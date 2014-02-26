#!/usr/bin/env python2

INDEX_DIR = "Movies.index"

import sys, os, lucene, re

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import IndexReader
from org.apache.lucene.search import IndexSearcher, BooleanQuery, BooleanClause, NumericRangeQuery
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.document import Field, StringField


"""
This scripts will prepare a CSV for Cassandra DB.
"""
def output_cassandra(line):
    regex = re.match(r"(?P<user_id>[0-9]+),(?P<movie_id>[0-9]+),(?P<score>.+)", line)
    if not regex:
        raise ValueError(line)
    user_id = regex.group("user_id")
    netflix_id = regex.group("movie_id")
    score = regex.group("score")

    query = QueryParser(Version.LUCENE_CURRENT, "netflix_id", analyzer).parse(netflix_id)

    scoreDocs = searcher.search(query, 1).scoreDocs
    if scoreDocs:
        doc = searcher.doc(scoreDocs[0].doc)
        movie_id = doc.getField("id").stringValue()
        print "{0},{1},{2}".format(user_id, movie_id, score)


if __name__ == '__main__':
    lucene.initVM()
    
    base_dir = os.path.abspath(os.path.curdir)
    index_file = os.path.join(base_dir, INDEX_DIR)
    store = SimpleFSDirectory(File(index_file))

    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
 
    reader = IndexReader.open(store)
    searcher = IndexSearcher(reader)   

    with open(sys.argv[1], 'r') as ratings:
        print "USE recommender;"
        for line in ratings:
            output_cassandra(line)

