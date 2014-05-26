filmyou-web
===========

scripts
-------

These scripts can help you in deploying FilmYou.

You need Netflix Prize dataset and some IMDB dataset (e.g., the one provided by TheOMDbAPI).

Just follow the order of execution of the Makefile.

Lucene index can be generated using `scripts/build_index.py` script.

The relational database can be populated using the resulting CSVs of `scripts/to_postgresql.py` and `scripts/update_votes.py` scripts.

Cassandra ratings can be obtained from Netflix database using `scripts/to_cassandra.py`.

`users_django.py` script requires special instructions. For more information, see the script documentation.
