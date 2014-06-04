# -*- coding: utf-8 -*-

from __future__ import absolute_import

import autocomplete_light

autocomplete_light.autodiscover()

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin

from . import views


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', views.HomeView.as_view(), name='home'),
    url('', include('apps.utils.urls')),
    url(r'^films/', include('apps.films.urls', namespace='films')),
    url(r'^reviews/', include('apps.reviews.urls', namespace='reviews')),
    url(r'^messages/', include('apps.messages.urls')),
    url(r'^accounts/', include('userena.urls')),
    url(r'^messages/', include('userena.contrib.umessages.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
)

urlpatterns += static('media', document_root=settings.MEDIA_ROOT)
urlpatterns += static('static', document_root=settings.STATIC_ROOT)

