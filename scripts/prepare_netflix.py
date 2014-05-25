#!/usr/bin/env python2

# -*- coding: utf-8 -*-

import os
import re
import pickle


def write_ratings(film, user_mapping):
    """
    This script runs over training_set folder of Netflix prize and
    builds a single CSV file with all the recommendations with the
    following format:
        user_id,film_netflix_id,rating
        <int,int,float>
    user_id is rebuilt from scratch.
    """
    first = film.next()
    film_id = int(first[:first.index(":")])
    for rating in film:
        regex = re.match(r"(?P<user_id>[0-9]+),(?P<score>[1-5]),(?P<date>.*)", rating)
        user_id = int(regex.group("user_id"))
        score = float(regex.group("score"))

        if user_id not in user_mapping:
            user_mapping[user_id] = len(user_mapping) + 1

        print "{0},{1},{2}".format(user_mapping[user_id], film_id, score)


if __name__ == '__main__':
    folder = os.path.join(".", "training_set")

    user_mapping = {}

    for f in os.listdir(folder):
        with open(os.path.join(folder, f), 'r') as film:
            write_ratings(film, user_mapping)

    with open('user_mapping.pkl', 'wb') as output:
        pickle.dump(user_mapping, output, -1)
