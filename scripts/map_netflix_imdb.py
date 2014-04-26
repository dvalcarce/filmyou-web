#!/usr/bin/env python2

INDEX_DIR = "Films.index"

import sys
import os
import re

import lucene

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import IndexReader, IndexWriter, IndexWriterConfig, Term
from org.apache.lucene.search import IndexSearcher, BooleanQuery, BooleanClause, NumericRangeQuery
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.document import Field, StringField


"""
This script will try to map netflix id's to IMDB ones.
Mismatchings between IMDB and Netflix collection are ignored.
A film titles file is required.
Lucene index will be updated with netflix ids.
"""


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

    if scoreDocs:
        if scoreDocs[0].score > 1.5:
            doc = searcher.doc(scoreDocs[0].doc)
            doc_id = doc.getField("id").stringValue()
            doc.add(StringField("netflix_id", str(netflix_id), Field.Store.YES))
            writer.updateDocument(Term("id", doc_id), doc)


if __name__ == '__main__':
    lucene.initVM()

    if len(sys.argv) < 2:
        print "{0} <titles_file>".format(sys.argv[0])
        sys.exit(0)

    base_dir = os.path.abspath(os.path.curdir)
    index_file = os.path.join(base_dir, INDEX_DIR)
    store = SimpleFSDirectory(File(index_file))

    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

    reader = IndexReader.open(store)
    searcher = IndexSearcher(reader)

    writer_config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
    writer_config.setOpenMode(IndexWriterConfig.OpenMode.APPEND)
    writer = IndexWriter(store, writer_config)

    with open(sys.argv[1], 'r') as titles:
        for line in titles:
            do_mapping(line)

    writer.commit()
