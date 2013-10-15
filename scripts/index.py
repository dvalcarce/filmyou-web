#!/usr/bin/env python

INDEX_DIR = "Movies.index"

import sys, os, lucene, re, csv, time, calendar

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField, IntField, LongField, FloatField, StringField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

"""
This script scans all IMDB collection and builds PyLucene index.
The following format is assumed:

    ID  imdbID  Title   Year    Rating  Runtime Genre   Released    DirectorWriter  Cast    imdbRating  imdbVotes   Poster  Plot    FullPlot    lastUpdated

"""
class IndexMovies(object):
    """Usage: python index.py <imdb_tsv>"""

    def __init__(self, root, storeDir, analyzer):
        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs(root, writer)
        writer.commit()
        writer.close()

    def indexDocs(self, root, writer):
        print "Building index..."
        with open(root, "r") as tsv:
            for row in csv.reader(tsv, delimiter='\t'):
                try:
                    doc = Document()
                    doc.add(StringField("id", row[0], Field.Store.YES))
                    doc.add(TextField("title", row[2], Field.Store.YES))
                    doc.add(IntField("year", self.parse_int(row[3]), Field.Store.YES))
                    doc.add(StringField("rating", row[4], Field.Store.YES))
                    doc.add(IntField("runtime", self.parse_runtime(row[5]), Field.Store.YES))
                    self.add_elements(doc, row[6], "genre", StringField)
                    doc.add(LongField("released", self.parse_date(row[7]), Field.Store.YES))
                    self.add_elements(doc, row[8], "director", TextField)
                    self.add_elements(doc, row[9], "writer", TextField)
                    self.add_elements(doc, row[10], "cast", TextField)
                    doc.add(FloatField("imdb_rating", self.parse_float(row[11]), Field.Store.YES))
                    doc.add(IntField("imdb_votes", self.parse_int(row[12]), Field.Store.YES))
                    doc.add(StringField("poster", row[13], Field.Store.YES))
                    doc.add(TextField("plot", row[14], Field.Store.YES))
                    doc.add(TextField("fullplot", row[15], Field.Store.YES))
                    doc.add(LongField("updated", self.parse_date(row[16]), Field.Store.YES))
                    writer.addDocument(doc)
                except:
                    sys.stderr.write("ROW -> " + ",".join(row) + "\n")

        print "Index completed"

    def parse_int(self, text):
        try:
            return int(text)
        except ValueError:
            return -1

    def parse_float(self, text):
        try:
            return int(text)
        except ValueError:
            return -1.0

    def parse_runtime(self, text):
        regex = re.match(r"((?P<hours>[0-9]+)\s*h)?\s*((?P<minutes>[0-9]+)\s*min)?", text)
        if not regex:
            return -1
        hours = regex.group("hours")
        minutes = regex.group("minutes")
        if not minutes:
            minutes = 0
        else:
            minutes = int(minutes)
        if hours:
            minutes += int(hours) * 60
        return minutes

    def parse_date(self, text):
        if text == "N/A" or text == "":
            return -2**63       # Java Long.MIN_VALUE
        t = time.strptime(text, r"%Y-%m-%d")
        return long(calendar.timegm(t))

    def add_elements(self, doc, text, name, field):
        if text == "N/A" or text == "":
            return doc.add(field(name, text, Field.Store.YES))
        for element in text.split(", "):
            doc.add(field(name, element, Field.Store.YES))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "{0} <imdb_tsv>".format(sys.argv[0])
        sys.exit(1)
    lucene.initVM()
    try:
        base_dir = os.path.abspath(os.path.curdir)
        IndexMovies(sys.argv[1], os.path.join(base_dir, INDEX_DIR), StandardAnalyzer(Version.LUCENE_CURRENT))
    except Exception as e:
        print e
