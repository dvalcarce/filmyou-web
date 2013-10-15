#!/usr/bin/env python

import sys

"""
This script will prepare CQL INSERT statements for Cassandra DB.
"""
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "{0} <ratings>".format(sys.argv[0])
		sys.exit(0)

	with open(sys.argv[1], 'r') as data:
	    print "USE recommender;"
	    for line in data:
	        cql = "INSERT INTO ratings (user, movie, score) VALUES ({0});".format(line[:-1])
	        print cql

