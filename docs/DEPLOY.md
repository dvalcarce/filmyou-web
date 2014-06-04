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

For the storage engine, the following software is tested:
- PostgreSQL 9.1 or higher (you must create filmyou database)
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


### PostgreSQL Schema

After creating `filmyou` database, run the following commands to initialise tables and indexes:

```
$ python manage.py syncdb
$ python manage.py migrate
$ python manage.py check_permissions
```

Add some default properties:

```
SET datestyle = "ISO, DMY";
ALTER TABLE films_film ALTER COLUMN n_votes SET DEFAULT 0;
ALTER TABLE films_film ALTER COLUMN sum_votes SET DEFAULT 0.0;
```

#### Autocompletion Optimization

Add GIN indexes to speed up ILIKE queries:

```
CREATE EXTENSION pg_trgm;
CREATE INDEX "films_person_name_gin" ON "films_person" USING GIN ("name");
CREATE INDEX "films_genre_name_gin" ON "films_genre" USING GIN ("name");
CREATE INDEX "films_country_name_gin" ON "films_country" USING GIN ("name");
CREATE INDEX "films_language_name_gin" ON "films_language" USING GIN ("name");
```

We need to change Django ORM behaviour:
- Replace 'LIKE UPPER(%s)' with 'ILIKE %s' and `UPPER(%s)` with `ILIKE %s` in `/path/to/site-packages/django/db/backends/postgresql_psycopg2/base.py`.
- Comment the following lines in `/path/to/site-packages/django/db/backends/postgresql_psycopg2/operations.py`:
```
    if lookup_type in ('iexact', 'icontains', 'istartswith', 'iendswith'):chr
        lookup = 'UPPER(%s)' % lookup
```

### Cassandra Schema

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
