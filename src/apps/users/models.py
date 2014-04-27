from django.contrib.auth.models import User

from apps.films.models import Film
from libs.cassandra import CassandraAdapter


__author__ = 'daniel'


class MyUser(User):
    class Meta:
        proxy = True

    def get_rate_for_films(self, films):
        """
        Returns the rates for the given films in a 'zipped way':
            [(film1, rate1), (film2, rate2)...]
        """
        rates = []
        for film in films:
            query = "SELECT item, score FROM ratings WHERE user = %(user)s AND item = %(film)s"
            parameters = {
                'user': self.id,
                'film': int(film.film_id),
            }
            with CassandraAdapter() as db:
                results = db.execute(query, parameters)
            if results:
                rates.append(results[0][1])
            else:
                rates.append(None)

        # Commentend until bug CASSANDRA-6137 is resolved

        # query = "SELECT item, score FROM ratings WHERE user = :user AND item IN :films"
        # parameters = {
        #     'user': self.id,
        #     'films': tuple(sorted(tuple(int(film.film_id) for film in films))),
        # }
        # with CassandraAdapter() as db:
        #     results = dict(db.execute(query, parameters))

        # rates = []
        # for film in films:
        #     if film.film_id in results:
        #         rates.append(results[film.film_id])
        #     else:
        #         rates.append(None)

        return zip(films, rates)

    def get_ratings(self, last=None, n_results=10):
        """
        Returns a list of rated films by self:
            [(film1, rate1), (film2, rate2)...]
        """
        parameters = {
            'user': self.id,
            'limit': n_results
        }
        if last:
            query = "SELECT item, score " \
                    "FROM ratings " \
                    "WHERE user = %(user)s AND item > %(last)s " \
                    "LIMIT " \
                    "%(limit)s"
            parameters['last'] = last
        else:
            query = "SELECT item, score " \
                    "FROM ratings " \
                    "WHERE user = %(user)s " \
                    "LIMIT %(limit)s"

        with CassandraAdapter() as db:
            result = db.execute(query, parameters)

        return [
            (Film.objects.get(film_id=film), score) for (film, score) in
            result
        ]

    def get_recommendations(self, last=None, n_results=10):
        """
        Get recommendations for self from Cassandra DB:
            [(film1, predicted_rate1), (film2, predicted_rate2)...]
        """
        parameters = {
            'user': self.id,
            'limit': n_results
        }

        if last:
            query = "SELECT item, relevance " \
                    "FROM recommendations " \
                    "WHERE user = %(user)s AND item > " \
                    "%(last)s LIMIT " \
                    "%(limit)s"
            parameters['last'] = last
        else:
            query = "SELECT item, relevance " \
                    "FROM recommendations " \
                    "WHERE user = %(user)s " \
                    "LIMIT %(limit)s"

        with CassandraAdapter() as db:
            result = db.execute(query, parameters)

        return [
            (Film.objects.get(film_id=film), score) for (film, score) in
            result
        ]

    def rate(self, film, score):
        """
        Inserts new rating in Cassandra DB.
        """
        query = "INSERT INTO ratings (user, item, score) " \
                "VALUES (:user, :item, :score)"
        parameters = {
            'user': self.id,
            'item': film.film_id,
            'score': float(score)
        }

        with CassandraAdapter() as db:
            db.execute(query, parameters)