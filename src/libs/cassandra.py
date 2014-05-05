# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf import settings

from cassandra.cluster import Cluster


class CassandraConnection(object):
    """
    Open a connection to Cassandra allowing query execution.
    """

    def __enter__(self):
        host = settings.CASSANDRA['HOST']
        port = int(settings.CASSANDRA['PORT'])
        keyspace = settings.CASSANDRA['KEYSPACE']
        cluster = Cluster([host], port=port, compression=True)
        self.session = cluster.connect(keyspace)

        return self

    def execute(self, query, parameters):
        """
        Run a CQL query with the given parameters.

        Example:
            query = "SELECT column FROM cf WHERE name = %(name)s"
            parameters = { 'name' = "Foo" }
        will run:
            SELECT column FROM cf WHERE name = 'Foo'

        :param query: query
        :param parameters: dict parameters
        :return: a list of named tuples
        """
        return self.session.execute(query, parameters)

    def __exit__(self, type, value, traceback):
        self.session.cluster.shutdown()
        self.session.shutdown()
