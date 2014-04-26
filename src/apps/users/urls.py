# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.users.views',
    url(r'^(?P<username>[0-9A-Za-z]+)/$', 'details', name='details'),
)
