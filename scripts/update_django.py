#!/usr/bin/env python2

import sys

film_TABLE = "filmyou_film"

"""
This script will prepare SQL UPDATE statements for film model in Django.
This will add n_votes and sum_votes fields.
"""
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "{0} <ratings>".format(sys.argv[0])
        sys.exit(0)

    with open(sys.argv[1], 'r') as data:
        films = {}
        for line in data:
            user, film, score = line[:-1].split(",")
            user = int(user)
            film = int(film)
            score = float(score)
            n_votes, sum_votes = films.get(film, (0, 0.0))
            films[film] = (n_votes + 1, sum_votes + score)

    for film in films:
        n_votes, sum_votes = films[film]
        print "UPDATE {table} SET n_votes = {n_votes}, sum_votes = {sum_votes} WHERE film_id = {film};".format(
            table=film_TABLE,
            n_votes=n_votes,
            sum_votes=sum_votes,
            film=film
        )
