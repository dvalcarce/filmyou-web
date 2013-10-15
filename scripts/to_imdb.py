#!/usr/bin/env python

import os
import sys
import re

"""
This script reads a mapping csv and transform netflix ratings to 
IMDB ratings. If there is no matching, the rating is ignored.
"""
def get_mapping(mapping):
	m = {}
	try:
		for line in mapping:
			regex = re.match(r"(?P<netflix>[0-9]+),(?P<imdb>[0-9]+)", line)
			netflix_id = regex.group("netflix")
			imdb_id = regex.group("imdb")
			m[netflix_id] = imdb_id
		return m
	except Exception as e:
		raise ValueError(e)


def to_imdb(mapping, csv):
	m = get_mapping(mapping)
	try:
		for line in csv:
			regex = re.match(r"(?P<user>[0-9]+),(?P<movie>[0-9]+),(?P<rating>.*)", line)
			user = regex.group("user")
			movie = regex.group("movie")
			rating = regex.group("rating")
			if movie in m:
				print "{0},{1},{2}".format(user, m[movie], float(rating))
	except Exception as e:
		raise ValueError(e)


if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "{0} <mapping> <netflix_csv>".format(sys.argv[0])
		sys.exit(0)

	with open(sys.argv[1], "r") as mapping, open(sys.argv[2], "r") as csv: 
		to_imdb(mapping, csv)
