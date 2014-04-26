# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'apps.films.views',
    url(r'^(?P<film_id>[0-9]+)/$', 'details', name='details'),
    url(r'^recommendations/$', 'recommendations', name='recommendations'),
    url(r'^ratings/$', 'ratings', name='ratings'),

    url(r'^rate/$', 'rate', name='rate'),

    url(r'^search/advanced/$', 'advanced_search', name='advanced_search'),
    url(r'^search/$', 'search', name='search'),
)
