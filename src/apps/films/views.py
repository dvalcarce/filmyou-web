# -*- coding: utf-8 -*-

from __future__ import absolute_import

from os import path
import urllib
import json

from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.generic import View, FormView
from django.views.generic.detail import DetailView
from braces.views import LoginRequiredMixin

from apps.reviews.forms import ReviewForm
from apps.utils import search
from apps.utils.db import retrieve_with_related_or_404
from libs.lucene import FilmSearcher
from .models import Film
from .forms import SearchForm


app_name = Film._meta.app_label


class FilmDetails(DetailView):
    model = Film

    def get_object(self, queryset=None):
        film = retrieve_with_related_or_404(Film, int(self.kwargs['pk']))
        if self.request.user.is_authenticated():
            film.set_preference(self.request.user.profile)

        return film

    def get_context_data(self, **kwargs):
        context = super(FilmDetails, self).get_context_data(**kwargs)
        context['form'] = ReviewForm()
        return context


class Search(View):
    template_name = path.join(app_name, "film_list.html")
    page_template = path.join(app_name, "film_page.html")

    def _get_next(self, films):
        if films:
            url = "{base}?last_id={last_id}&last_score={last_score}&".format(
                base=reverse('films:search'),
                last_id=films[-1].doc_id,
                last_score=films[-1].doc_score)

            return url + urllib.urlencode(self.query)

    def get(self, *args, **kwargs):
        self.query = search.prepare_query(self.request)

        if self.request.is_ajax():
            return self._search_ajax()

        with FilmSearcher() as searcher:
            films = searcher.query(self.query)

        if films and self.request.user.is_authenticated():
            films = self.request.user.profile.get_preferences_for_films(films)

        c = {
            'page_template': self.page_template,
            'query': self.query,
            'next': self._get_next(films),
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
            films = self.request.user.profile.get_preferences_for_films(films)

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


def rate(request):
    """
    Rate a film via AJAX.
    """
    if request.is_ajax():
        current = request.POST['current']
        if request.user.is_authenticated():
            film_id = int(request.POST['film'])
            score = float(request.POST['score'])

            film = Film.objects.get(film_id=film_id)
            film.rate(request.user.profile, score)

            return HttpResponse()
        else:
            response = settings.LOGIN_URL + "?next=" + current
            return HttpResponse(response)
    else:
        raise PermissionDenied


class Recommendations(LoginRequiredMixin, View):
    template = path.join(app_name, 'film_list.html')
    page_template = path.join(app_name, 'film_page.html')

    def _get_next(self, films):
        if films:
            return reverse('films:recommendations') \
                   + '?last_item=' + str(films[-1].film_id) \
                   + '&last_relevance=' + str(films[-1].relevance)

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
            last = (float(self.request.GET['last_relevance']), int(self.request.GET['last_item']))
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
    profile = request.user.profile

    reviews = profile.review_set.all().prefetch_related("film")[:4]
    films = {review.film for review in reviews}
    profile.get_preferences_for_films(films)

    c = {
        'suggestions': profile.get_recommendations(count=4),
        'reviewed': reviews
    }

    return render(request, template, c)

