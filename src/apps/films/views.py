# -*- coding: utf-8 -*-

from __future__ import absolute_import

from os import path
import urllib

from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.views.generic import View, FormView
from django.views.generic.detail import DetailView
from braces.views import LoginRequiredMixin

from libs.search import FilmSearcher
from .models import Film
from .forms import SearchForm


app_name = Film._meta.app_label


class FilmDetails(DetailView):
    model = Film

    def get_object(self, queryset=None):
        film = super(FilmDetails, self).get_object(queryset)
        if self.request.user.is_authenticated():
            film.set_preference(self.request.user.profile)

        return film


class Search(View):
    template_name = path.join(app_name, "film_list.html")
    page_template = path.join(app_name, "film_page.html")

    def _retrieve_int(self, querydict, key):
        try:
            return int(querydict.pop(key)[0])
        except ValueError or KeyError:
            return None

    def _get_next(self, query, films):
        if films:
            url = "{base}?last_id={last_id}&last_score={last_score}&".format(
                base=reverse('films:search'),
                last_id=films[-1].doc_id,
                last_score=films[-1].doc_score)

            return url + urllib.urlencode(query)

    def _get_query_terms(self):
        query = self.request.GET.copy()
        query.pop('last_id', None)
        query.pop('last_score', None)

        if 'year_start' in query or 'year_end' in query:
            year_start = self._retrieve_int(query, 'year_start')
            year_end = self._retrieve_int(query, 'year_end')

            if year_start or year_end:
                year_start = "0" if year_start is None else year_start
                year_end = "50000" if year_end is None else year_end
                query['year'] = "{0},{1}".format(year_start, year_end)

        ending = "-autocomplete"
        d = []
        for (k, values) in query.lists():
            k = k.encode('utf-8')
            if k.endswith(ending):
                k = k[:k.rindex(ending)]
            for v in values:
                v = v.encode('utf-8')
                if v:
                    d.append((k, v))

        return d

    def get(self, *args, **kwargs):
        self.query = self._get_query_terms()

        if self.request.is_ajax():
            return self._search_ajax()

        with FilmSearcher() as searcher:
            films = searcher.query(self.query)

        if films and self.request.user.is_authenticated():
            films = self.request.user.profile.get_preferences_for_films(films)

        c = {
            'page_template': self.page_template,
            'query': self.query,
            'next': self._get_next(self.query, films),
            'films': films,
            'title': _("Search results")
        }

        return render(self.request, self.template_name, c)

    def _search_ajax(self):
        last_id = int(self.request.GET['last_id'])
        last_score = float(self.request.GET['last_score'])
        with FilmSearcher() as searcher:
            films = searcher.query_after(self.query, last_id, last_score)

        if not films:
            return HttpResponse()

        if self.request.user.is_authenticated():
            user = User.objects.get(username=self.request.user.username)
            films = user.profile.get_preferences_for_films(films)

        c = {
            'films': films,
            'next': self._get_next(self.query, films),
        }

        return render(self.request, self.page_template, c)


class AdvancedSearch(FormView):
    template_name = path.join(app_name, "advanced_search.html")
    form_class = SearchForm


class Ratings(LoginRequiredMixin, View):
    template_name = path.join(app_name, "film_list.html")
    page_template = path.join(app_name, "film_page.html")

    def _get_next(self, films):
        if films:
            return reverse('films:ratings') + '?last=' + str(films[-1].film_id)

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            return self._ratings_ajax()

        ratings = self.request.user.profile.get_rated_films()

        c = {
            'page_template': self.page_template,
            'films': ratings,
            'next': self._get_next(ratings),
            'title': _("My ratings")
        }

        return render(self.request, self.template_name, c)

    def _ratings_ajax(self):
        try:
            last = int(self.request.GET['last'])
        except:
            return HttpResponse("")

        ratings = self.request.user.profile.get_rated_films(last)

        if ratings:
            c = {
                'films': ratings,
                'next': self._get_next(ratings),
            }

            return render(self.request, self.page_template, c)
        else:
            return HttpResponse()


@login_required
def rate(request):
    """
    Rate a film via AJAX.
    """
    if request.is_ajax():
        film_id = int(request.GET['film'])
        score = float(request.GET['score'])

        film = Film.objects.get(film_id=film_id)
        film.rate(request.user.profile, score)

        return HttpResponse()
    else:
        raise PermissionDenied


class Recommendations(LoginRequiredMixin, View):
    template = path.join(app_name, 'film_list.html')
    page_template = path.join(app_name, 'film_page.html')

    def _get_next(self, films):
        if films:
            return reverse('films:recommendations') \
                   + '?last_item=' + str(films[-1].film_id) \
                   + '?last_relevance=' + str(films[-1].relevance)

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            return self._recommendations_ajax()

        recommendations = self.request.user.profile.get_recommendations()

        c = {
            'page_template': self.page_template,
            'films': recommendations,
            'next': self._get_next(recommendations),
            'title': _("Suggestions")
        }

        return render(self.request, self.template, c)

    def _recommendations_ajax(self):
        try:
            last = int(self.request.GET['last'])
        except:
            return HttpResponse("")

        recommendations = self.request.user.profile.get_recommendations(last)

        if recommendations:
            c = {
                'films': recommendations,
                'next': self._get_next(recommendations),
            }

            return render(self.request, self.page_template, c)
        else:
            return HttpResponse()


def render_homepage(request):
    template = path.join(app_name, 'home.html')
    return HttpResponse()