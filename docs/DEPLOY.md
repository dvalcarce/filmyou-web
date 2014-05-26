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

Note: PyLucene requires manual installation.

Persistence
-----------

For the storage engine, the following software is used:
- PostgreSQL 9.3 or higher (you must create filmyou database)
- Apache Cassandra 2.0.5 or higher
- Apache Lucene 4.6 or higher

Configure the environment variables:
- RDBMS_USER: PostgreSQL user login
- RDBMS_PASSWORD: PostgreSQL user password
- RDBMS_HOST: PostgreSQL IP address
- RDBMS_PORT: PostgreSQL port
- CASSANDRA_HOST: Cassandra IP address
- CASSANDRA_PORT: Cassandra port
- CASSANDRA_KEYSPACE: Cassandra keyspace
- LUCENE_PATH: Path to Lucene index

After creating filmyou database, run the following commands to initialise tables and indexes:

```
$ python manage.py syncdb
$ python manage.py migrate
$ python manage.py check_permissions
```

Now introduce the following sentences in a Cassandra CQL Shell:

```
CREATE KEYSPACE recommender
WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor': 3};

USE recommender;

CREATE TABLE ratings (
    user int,
    item int,
    score float,
    PRIMARY KEY (user, item)
);

CREATE TABLE recommendations (
    user int,
    relevance float,
    item int,
    cluster int,
    PRIMARY KEY (user, relevance, item)
) WITH CLUSTERING ORDER BY (relevance DESC, item ASC);

CREATE INDEX recommendations_item ON recommendations (item);
```

Initial data
------------

In general, `scripts` folder contains a bunch of useful tools for generating initial data. See `scripts/README.md` for more info.

