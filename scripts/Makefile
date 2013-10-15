
MOVIE_TITLES=movie_titles.txt
IMDB_TSV=omdb.tsv

NETFLIX_RATINGS=netflix.csv
MAPPING_CSV=mapping.csv
IMDB_RATINGS=imdb.csv
CQL_STATEMENTS=cassandra.cql
SQL_STATEMENTS=postgresql.sql
UPDATE_STATEMENTS=update.sql

all: netflix pylucene mapping transform cql sql movies

netflix:
	@echo "Merge all netflix ratings in one file (netflix.csv)"
	python prepare_netflix.py > $(NETFLIX_RATINGS)

pylucene: $(IMDB_TSV)
	@echo "Build PyLucene Index with all IMDB info"
	python index.py $(IMDB_TSV)

mapping: $(MOVIE_TITLES)
	@echo "Do mapping between netflix and IMDB id's using PyLucene Index"
	python map_netflix_imdb.py $(MOVIE_TITLES) > $(MAPPING_CSV)

transform:
	@echo "Transform netflix ratings to IMDB ones"
	python to_imdb.py $(MAPPING_CSV) $(NETFLIX_RATINGS) > $(IMDB_RATINGS)

cql:
	@echo "Generate CQL statements for ratings"
	python to_cassandra.py $(IMDB_RATINGS) > $(CQL_STATEMENTS)

sql:
	@echo "Generate SQL statements for movie info"
	python to_postgresql.py $(IMDB_TSV) > $(SQL_STATEMENTS)

movies:
	@echo "Generate UPDATE statements for movies(n_votes, sum_votes)"
	python update_django.py $(IMDB_RATINGS) > $(UPDATE_STATEMENTS)

clean:
	rm -f $(NETFLIX_RATINGS) $(MAPPING_CSV) $(IMDB_RATINGS) $(CQL_STATEMENTS) $(SQL_STATEMENTS) $(UPDATE_STATEMENTS)
