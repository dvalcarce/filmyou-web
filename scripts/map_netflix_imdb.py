#!/usr/bin/env python

INDEX_DIR = "Movies.index"

import sys, os, lucene, re

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import IndexReader
from org.apache.lucene.search import IndexSearcher, BooleanQuery, BooleanClause, NumericRangeQuery
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

"""
This script will try to map netflix id's to IMDB ones.
Mismatchings between IMDB and Netflix collection are ignored.
A movie titles file is required.
"""
def scan(searcher, analyzer, titles):
    for line in titles:
        do_mapping(line)


def do_mapping(line):
    regex = re.match(r"(?P<netflix_id>[0-9]+),(?P<year>([0-9]+)|NULL),(?P<title>.+)", line)
    if not regex:
        raise ValueError(line)
    netflix_id = int(regex.group("netflix_id"))

    title = QueryParser.escape(regex.group("title"))
    query1 = QueryParser(Version.LUCENE_CURRENT, "title", analyzer).parse(title)

    year = regex.group("year")
    if year == "NULL":
        scoreDocs = searcher.search(query1, 1).scoreDocs
    else:
        year = int(year)

        query2 = NumericRangeQuery.newIntRange("year", year, year, True, True)
        booleanQuery = BooleanQuery();
        booleanQuery.add(query1, BooleanClause.Occur.MUST);
        booleanQuery.add(query2, BooleanClause.Occur.MUST);

        scoreDocs = searcher.search(booleanQuery, 1).scoreDocs

    for scoreDoc in scoreDocs:
        if scoreDoc.score > 1.5:
            doc = searcher.doc(scoreDoc.doc)
            doc_id = doc.getField("id")
            imdb_id = int(doc_id.stringValue())
            print "{0},{1}".format(netflix_id, imdb_id)
            return 

    # Mapping not found
    return
    

if __name__ == '__main__':
    lucene.initVM()
    
    if len(sys.argv) < 2:
        print "{0} <titles_file>".format(sys.argv[0])
        sys.exit(0)

    base_dir = os.path.abspath(os.path.curdir)
    index_file = os.path.join(base_dir, INDEX_DIR)
    index = SimpleFSDirectory(File(index_file))
    reader = IndexReader.open(index)
    
    searcher = IndexSearcher(reader)
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

    with open(sys.argv[1], 'r') as titles:
        scan(searcher, analyzer, titles)
