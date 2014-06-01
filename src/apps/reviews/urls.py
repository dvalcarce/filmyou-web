# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf.urls import patterns, url

from apps.reviews.views import Reviews, CreateReview, RemoveReview

urlpatterns = patterns(
    '',
    url(r'^create/(?P<pk>[0-9]+)/$', CreateReview.as_view(), name='create'),
    url(r'^list/$', Reviews.as_view(), name='list'),
    url(r'^remove/(?P<pk>[0-9]+)/$', RemoveReview.as_view(), name='remove')
)

