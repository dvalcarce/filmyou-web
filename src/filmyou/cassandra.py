import cql

from django.conf import settings

class CassandraAdapter(object):
    """
    This class allows to communicate easily with Cassandra DB.
    """
    def __enter__(self):
        host = settings.CASSANDRA['HOST']
        port = settings.CASSANDRA['PORT']
        keyspace = settings.CASSANDRA['KEYSPACE']
        self.connection = cql.connect(host, port, keyspace, cql_version='3.0.0')
        self.cursor = self.connection.cursor()
        return self

    def execute(self, query, parameters):
        """
        Run a CQL query with the given parameters.

        Example:
            query = "SELECT column FROM CF WHERE name=:name"
            parameters = { 'name' = "Foo" }
        will run:
            SELECT column FROM CF WHERE name=:Foo
        """
        self.cursor.execute(query, parameters)
        return list(self.cursor)

    def _cursor_generator(self):
        for row in self.cursor:
            yield row

    def __exit__(self, type, value, traceback):
        self.cursor.close()
        self.connection.close()
