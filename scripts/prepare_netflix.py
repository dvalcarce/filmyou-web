#!/usr/bin/env python

import os, re

"""
This script runs over training_set folder of Netflix prize and
builds a single CSV file with all the recommendations with the
following format:
	user_id,movie_netflix_id,rating
	<int,int,float>
"""
def write_ratings(movie):
	first = movie.next()
	movie_id = int(first[:first.index(":")])
	for rating in movie:
		regex = re.match(r"(?P<user_id>[0-9]+),(?P<score>[1-5]),(?P<date>.*)", rating)
		user_id = int(regex.group("user_id"))
		score = float(regex.group("score"))
		print "{0},{1},{2}".format(user_id, movie_id, score)


if __name__ == '__main__':
	folder = os.path.join(".", "training_set")
	for f in os.listdir(folder):
		with open(os.path.join(folder, f), 'r') as movie:
			write_ratings(movie)
