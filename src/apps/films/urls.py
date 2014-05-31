# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^details/(?P<pk>[0-9]+)/$', views.FilmDetails.as_view(), name='details'),

    url(r'^search/$', views.Search.as_view(), name='search'),
    url(r'^search/advanced/$', views.AdvancedSearch.as_view(), name='advanced_search'),

    url(r'^recommendations/$', views.Recommendations.as_view(), name='recommendations'),
    url(r'^ratings/$', views.Ratings.as_view(), name='ratings'),

    url(r'^rate/$', views.rate, name='rate'),
)