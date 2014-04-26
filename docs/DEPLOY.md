Deployment
==========

Install required python packages:

```
$ pip install -r requirements/production.txt
```

or

```
$ pip install -r requirements.txt
```

For the storage engine, the following software is required:
- PostgreSQL 8.4 or higher
- Apache Cassandra 2.0.5 or higher
- Apache Lucene 4.6 or higher


Configure the environment variables:
- RDBMS_USER
- RDBMS_PASSWORD
- RDBMS_HOST
- RDBMS_PORT
- CASSANDRA_HOST
- CASSANDRA_PORT
- CASSANDRA_KEYSPACE
- LUCENE_PATH

