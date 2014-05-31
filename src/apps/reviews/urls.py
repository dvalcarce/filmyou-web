# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf.urls import patterns, url

from apps.reviews.views import Reviews, CreateReview

urlpatterns = patterns(
    '',
    url('^create/(?P<pk>[0-9]+)/$', CreateReview.as_view(), name='create'),
    url('^list/$', Reviews.as_view(), name='list'),
)
