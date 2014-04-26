
FILM_TITLES=movie_titles.txt
IMDB_TSV=omdb.tsv
NETFLIX_RATINGS=netflix.csv
RATINGS=ratings.csv
SQL_STATEMENTS=sql
LUCENE_INDEX=Films.Index

all: netflix pylucene mapping cql sql

netflix:
	@echo "Merge all netflix ratings in one file (netflix.csv)"
	python2 prepare_netflix.py > $(NETFLIX_RATINGS)

lucene: $(IMDB_TSV)
	@echo "Build PyLucene Index with all IMDB info (Films.Index)"
	python2 build_index.py $(IMDB_TSV)

mapping: $(film_TITLES)
	@echo "Do mapping between netflix and IMDB id's using PyLucene Index"
	python2 map_netflix_imdb.py $(FILM_TITLES)

cql:
	@echo "Generate a CSV for Cassandra COPY command"
	python2 to_cassandra.py $(NETFLIX_RATINGS) > $(RATINGS)

sql:
	@echo "Generate TSV files for PostgreSQL \copy command"
	python2 to_postgresql.py

clean:
	rm -rf $(NETFLIX_RATINGS) $(LUCENE_INDEX) $(RATINGS) $(SQL_STATEMENTS)

