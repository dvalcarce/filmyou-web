#!/usr/bin/env python2

import sys

MOVIE_TABLE = "filmyou_movie"


"""
This script will prepare SQL UPDATE statements for Movie model in Django.
This will add n_votes and sum_votes fields.
"""
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "{0} <ratings>".format(sys.argv[0])
        sys.exit(0)

    with open(sys.argv[1], 'r') as data:
        movies = {}
        for line in data:
            user, movie, score = line[:-1].split(",")
            user = int(user)
            movie = int(movie)
            score = float(score)
            n_votes, sum_votes = movies.get(movie, (0, 0.0))
            movies[movie] = (n_votes + 1, sum_votes + score)

    for movie in movies:
        n_votes, sum_votes = movies[movie]
        print "UPDATE {table} SET n_votes = {n_votes}, sum_votes = {sum_votes} WHERE movie_id = {movie};".format(
            table=MOVIE_TABLE,
            n_votes=n_votes,
            sum_votes=sum_votes,
            movie=movie
        )
