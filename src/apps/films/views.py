# -*- coding: utf-8 -*-


from __future__ import absolute_import

from os import path

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.views.generic.detail import DetailView
from braces.views import LoginRequiredMixin

from libs.search import FilmSearcher
from .models import Film, MyUser


app_name = Film._meta.app_label


class FilmDetails(DetailView):
    model = Film

    def get_object(self, queryset=None):
        film = super(FilmDetails, self).get_object(queryset)
        film.set_preference(self.request.user)

        return film


class Search(View):
    template_name = path.join(app_name, "film_list.html")
    page_template = path.join(app_name, "film_page.html")

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            return self._search_ajax()

        query = self.request.GET.get('title', None)
        if query:
            with FilmSearcher() as searcher:
                films = searcher.query('title', query)
        else:
            films = []

        user = MyUser.objects.get(username=self.request.user.username)
        films = user.get_preferences_for_films(films)

        c = {
            'page_template': self.page_template,
            'query': query,
            'search': True,
            'films': films
        }

        return render_to_response(self.template_name, c,
                                  context_instance=RequestContext(self.request))

    def _search_ajax(self):
        try:
            last_id = self.request.GET['last_id']
            last_score = self.request.GET['last_score']
            query = self.request.GET['query']
        except:
            return HttpResponse("")

        with FilmSearcher() as searcher:
            results = searcher.query_after("title", query, last_id, last_score)

        if results:
            user = MyUser.objects.get(username=self.request.user.username)
            films = user.get_preferences_for_films(results)
            c = {
                'query': query,
                'films': films,
                'search': True
            }
        else:
            return HttpResponse("")

        return render_to_response(self.page_template, c,
                                  context_instance=RequestContext(self.request))


class SearchForm(View):
    template_name = path.join(app_name, "advanced_search.html")

    def get(self, request, *args, **kwargs):
        c = {
            'fields': [
                _("title"),
                _("genre"),
                _("director"),
                _("cast"),
                _("writer"),
                _("year"),
                _("runtime"),
                _("...")
            ]
        }

        return render_to_response(self.template_name, c,
                                  context_instance=RequestContext(self.request))


class Ratings(LoginRequiredMixin, View):
    template_name = path.join(app_name, "film_list.html")
    page_template = path.join(app_name, "film_page.html")

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            return self._ratings_ajax()

        user = MyUser.objects.get(username=self.request.user.username)
        ratings = user.get_rated_films()

        c = {
            'page_template': self.page_template,
            'films': ratings,
            'ratings': True
        }

        return render_to_response(self.template_name, c,
                                  context_instance=RequestContext(self.request))

    def _ratings_ajax(self):
        try:
            last = int(self.request.GET['last'])
        except:
            return HttpResponse("")

        user = MyUser.objects.get(username=self.request.user.username)
        ratings = user.get_rated_films(last)

        if ratings:
            c = {
                'films': ratings,
                'ratings': True
            }

            return render_to_response(self.page_template, c,
                                      context_instance=RequestContext(self.request))
        else:
            return HttpResponse("")


@login_required
def rate(request):
    """
    Rate a film via AJAX.
    """
    if request.is_ajax():
        film_id = int(request.GET['film'])
        score = float(request.GET['score'])

        user = MyUser.objects.get(username=request.user.username)
        film = Film.objects.get(film_id=film_id)
        film.rate(user, score)

        return HttpResponse("ok!")
    else:
        raise PermissionDenied


class Recommendations(LoginRequiredMixin, View):
    template = path.join(app_name, "film_list.html")
    page_template = path.join(app_name, "film_page.html")

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            return self._recommendations_ajax()

        user = MyUser.objects.get(username=self.request.user.username)
        recommendations = user.get_recommendations()

        c = {
            'page_template': self.page_template,
            'films': recommendations,
            'recommendations': True
        }

        return render_to_response(self.template, c,
                                  context_instance=RequestContext(self.request))

    def _recommendations_ajax(self):
        try:
            last = int(self.request.GET['last'])
        except:
            return HttpResponse("")

        user = MyUser.objects.get(username=self.request.user.username)
        recommendations = user.get_recommendations(last)

        if recommendations:
            c = {
                'films': recommendations,
                'recommendations': True
            }

            return render_to_response(self.page_template, c,
                                      context_instance=RequestContext(self.request))
        else:
            return HttpResponse("")
