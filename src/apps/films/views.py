# -*- coding: utf-8 -*-

from __future__ import absolute_import

from os import path
import urllib

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
        film.set_preference(self.request.user.profile)

        return film


class Search(View):
    template_name = path.join(app_name, "film_list.html")
    page_template = path.join(app_name, "film_page.html")

    def _get_next(self, films):
        if films:
            url = "{base}?last_id={last_id}&last_score={last_score}&".format(
                base=reverse('films:search'),
                last_id=films[-1].doc_id,
                last_score=films[-1].doc_score)

            query = self.request.GET.dict()
            query.pop('last_id', None)
            query.pop('last_score', None)

            return url + urllib.urlencode(self.request.GET)

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            return self._search_ajax()

        with FilmSearcher() as searcher:
            films = searcher.query(self.request.GET)

        if films and self.request.user.is_authenticated():
            films = self.request.user.profile.get_preferences_for_films(films)

        c = {
            'page_template': self.page_template,
            'query': self.request.GET,
            'next': self._get_next(films),
            'films': films,
            'title': "Search results"
        }

        return render(self.request, self.template_name, c)

    def _search_ajax(self):
        with FilmSearcher() as searcher:
            films = searcher.query_after(self.request.GET)

        if not films:
            return HttpResponse()

        if self.request.user.is_authenticated():
            user = User.objects.get(username=self.request.user.username)
            films = user.profile.get_preferences_for_films(films)

        c = {
            'films': films,
            'next': self._get_next(films),
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
            'title': "My ratings"
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
    template = path.join(app_name, "film_list.html")
    page_template = path.join(app_name, "film_page.html")

    def _get_next(self, films):
        if films:
            return reverse('films:recommendations') + '?last=' + str(films[-1].film_id)

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            return self._recommendations_ajax()

        recommendations = self.request.user.profile.get_recommendations()

        c = {
            'page_template': self.page_template,
            'films': recommendations,
            'next': self._get_next(recommendations),
            'title': "Recommendations"
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
