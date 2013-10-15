#!/usr/bin/env python

INDEX_DIR = "DB"

import sys, os, time, re, csv, time, calendar, psycopg2
from datetime import datetime


"""
This script scans OMDB collection and builds CSV files for PostgreSQL.
"""
class IndexMovies(object):
    def __init__(self, root, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        self.genres = {}
        self.people = {}
        self.indexDocs(root, storeDir)

    def indexDocs(self, root, storeDir):
        with open(os.path.join(storeDir, "movie.csv"), "w") as movie_file, \
            open(os.path.join(storeDir, "person.csv"), "w") as person_file, \
            open(os.path.join(storeDir, "genre.csv"), "w") as genre_file, \
            open(os.path.join(storeDir, "genre_movie.csv"), "w") as genre_movie_file, \
            open(os.path.join(storeDir, "director.csv"), "w") as director_file, \
            open(os.path.join(storeDir, "writer.csv"), "w") as writer_file, \
            open(os.path.join(storeDir, "cast.csv"), "w") as cast_file, \
            open(root, "r") as tsv:

            for row in csv.reader(tsv, delimiter='\t'):
                try:
                    self.movie_id = self.parse_int(row[0])
                    title = self.check_or_null(row[2])
                    year = self.parse_int(row[3])
                    runtime = self.parse_runtime(row[5])
                    rating = self.check_or_null(row[4])

                    released = self.parse_date(row[7])
                    plot = self.check_or_null(row[14])
                    fullplot = self.check_or_null(row[15])
                    poster = self.check_or_null(row[13])

                    self.parse_n_n(row[6], self.genres, genre_file, genre_movie_file)
                    self.parse_n_n(row[8], self.people, person_file, director_file)
                    self.parse_n_n(row[9], self.people, person_file, writer_file)
                    self.parse_n_n(row[10], self.people, person_file, cast_file)

                    movie_file.write("{id}\t{title}\t{year}\t{runtime}\t{rating}\t{released}\t{plot}\t{fullplot}\t{poster}\n".format(
                        id=self.movie_id,
                        title=title,
                        year=year,
                        runtime=runtime,
                        rating=rating,
                        released=released,
                        plot=plot,
                        fullplot=fullplot,
                        poster=poster)
                    )

                except Exception as e:
                    print repr(e)
                    print "ROW ->", row
                    print row[7]
                    print
                        

    def check_or_null(self, text):
        if text == "" or text == "N/A":
            return "NULL"
        else:
            return psycopg2.extensions.AsIs(text).getquoted()


    def parse_int(self, text):
        try:
            return int(text)
        except ValueError:
            return "NULL"

    def parse_n_n(self, text, entity, entity_f, relationship_f):
        if text == "N/A" or text == "":
            return
        for element in text.split(", "):
            try:
                entity_id = entity[element]
            except KeyError:
                entity_id = len(entity) + 1
                entity[element] = entity_id
                entity_f.write("{id}\t{name}\n".format(id=entity_id, name=element))

            relationship_f.write("{m}\t{g}\n".format(m=self.movie_id, g=entity_id))

    def parse_runtime(self, text):
        regex = re.match(r"((?P<hours>[0-9]+)\s*h)?\s*((?P<minutes>[0-9]+)\s*min)?", text)
        if not regex:
            return "NULL"
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
            return "NULL"
        t = time.strptime(text, r"%Y-%m-%d")
        ts = calendar.timegm(t)
        return "'{d}/{m}/{y}'".format(m=t.tm_mon, d=t.tm_mday, y=t.tm_year)


    def add_elements(self, doc, text, name, field):
        if text == "N/A" or text == "":
            return "NULL"
        for element in text.split(", "):
            doc.add(field(name, element, Field.Store.YES))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "{0} <movies file>".format(sys.argv[0])
        sys.exit(1)
    start = datetime.now()
    try:
        base_dir = os.path.abspath(os.path.curdir)
        IndexMovies(sys.argv[1], os.path.join(base_dir, INDEX_DIR))
        end = datetime.now()
        print 'time elapsed', end - start
    except Exception as e:
        print "Failed: ", e
        raise e

