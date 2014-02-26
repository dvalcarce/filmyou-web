
MOVIE_TITLES=movie_titles.txt
IMDB_TSV=omdb.tsv
NETFLIX_RATINGS=netflix.csv
MY_RATINGS=imdb.csv
CQL_STATEMENTS=ratings.csv
SQL_STATEMENTS=sql
LUCENE_INDEX=Movies.Index

all: netflix pylucene mapping cql sql

netflix:
	@echo "Merge all netflix ratings in one file (netflix.csv)"
	python2 prepare_netflix.py > $(NETFLIX_RATINGS)

lucene: $(IMDB_TSV)
	@echo "Build PyLucene Index with all IMDB info (Movies.Index)"
	python2 build_index.py $(IMDB_TSV)

mapping: $(MOVIE_TITLES) $(LUCENE_INDEX)
	@echo "Do mapping between netflix and IMDB id's using PyLucene Index"
	python2 map_netflix_imdb.py $(MOVIE_TITLES)

cql: $(LUCENE_INDEX)
	@echo "Generate a CSV for Cassandra COPY command"
	python2 to_cassandra.py $(NETFLIX_RATINGS)

sql: $(LUCENE_INDEX)
	@echo "Generate TSV files for PostgreSQL \copy command"
	python2 to_postgresql.py

clean:
	rm -rf $(NETFLIX_RATINGS) $(LUCENE_INDEX) $(CQL_STATEMENTS) $(SQL_STATEMENTS)

