#!/usr/bin/env python2

# -*- coding: utf-8 -*-

INDEX_DIR = "Films.index"

import sys
import os
import re
import csv
import time
import calendar
import codecs

import lucene

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField, IntField, LongField, FloatField, \
    StringField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version


class IndexFilms(object):
    """
    This script scans all IMDB collection and builds PyLucene index.
    The following format is assumed:

        ID  imdbID  Title   Year    Rating  Runtime Genre   Released
        Director    Writer  Cast    Metacritic  imdbRating  imdbVotes
        Poster  Plot    FullPlot    Language    Country     Awards
        lastUpdated

    Usage: python index.py <imdb_tsv>
    """

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
        my_id = 1
        with open(root, 'r') as tsv:
            for row in tsv.readlines()[1:]:
                row = row.translate(None, '\r\n').split("\t")

                doc = Document()
                doc.add(StringField("id", str(my_id), Field.Store.YES))
                doc.add(StringField("imdb_id", row[0], Field.Store.YES))
                doc.add(TextField("title", self.parse_string(row[2]), Field.Store.YES))
                doc.add(IntField("year", self.parse_int(row[3]), Field.Store.YES))
                doc.add(StringField("rating", self.parse_string(row[4]), Field.Store.YES))
                doc.add(IntField("runtime", self.parse_runtime(row[5]), Field.Store.YES))
                self.add_elements(doc, row[6], "genre", StringField)
                doc.add(LongField("released", self.parse_date(row[7]), Field.Store.YES))
                self.add_elements(doc, row[8], "director", TextField)
                self.add_elements(doc, row[9], "writer", TextField)
                self.add_elements(doc, row[10], "cast", TextField)
                doc.add(IntField("metascore", self.parse_int(row[11]), Field.Store.YES))
                doc.add(FloatField("imdb_rating", self.parse_float(row[12]), Field.Store.YES))
                doc.add(IntField("imdb_votes", self.parse_int(row[13]), Field.Store.YES))
                doc.add(StringField("poster", self.parse_string(row[14]), Field.Store.YES))
                doc.add(TextField("plot", self.parse_string(row[15]), Field.Store.YES))
                doc.add(TextField("fullplot", self.parse_string(row[-5]), Field.Store.YES))
                self.add_elements(doc, row[-4], "language", StringField)
                self.add_elements(doc, row[-3], "country", StringField)
                doc.add(IntField("awards", self.parse_awards(row[-2]), Field.Store.YES))
                doc.add(LongField("updated", self.parse_datetime(row[-1]), Field.Store.YES))
                writer.addDocument(doc)

                my_id += 1


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

    def parse_string(self, text):
        if text == "N/A":
            return ""
        return text.decode("latin-1")

    def parse_awards(self, text):
        regex = re.match(r".*(?P<awards>[0-9]+).*", text)
        if not regex:
            return -1
        return int(regex.group("awards"))

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
            return -2 ** 63  # Java Long.MIN_VALUE
        t = time.strptime(text, r"%Y-%m-%d")
        return long(calendar.timegm(t))

    def parse_datetime(self, text):
        if text == "N/A" or text == "":
            return -2 ** 63  # Java Long.MIN_VALUE
        try:
            idx = text.index(".")
            text = text[:idx]
        except ValueError:
            pass

        t = time.strptime(text, r"%Y-%m-%d %H:%M:%S")
        return long(calendar.timegm(t))

    def add_elements(self, doc, text, field_name, field_type):
        if text == "N/A" or text == "":
            return doc.add(field_type(field_name, "", Field.Store.YES))
        for element in text.split(", "):
            doc.add(field_type(field_name, element.decode("latin-1"), Field.Store.YES))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "{0} <imdb_tsv>".format(sys.argv[0])
        sys.exit(1)
    lucene.initVM()
    base_dir = os.path.abspath(os.path.curdir)
    IndexFilms(sys.argv[1], os.path.join(base_dir, INDEX_DIR),
               StandardAnalyzer(Version.LUCENE_CURRENT))
