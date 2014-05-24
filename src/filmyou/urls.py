# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from django.contrib import admin

from . import views


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', views.HomeView.as_view(), name='home'),
    url('', include('apps.utils.urls')),
    url(r'^films/', include('apps.films.urls', namespace='films')),
    url(r'^accounts/', include('userena.urls')),
    url(r'^messages/', include('userena.contrib.umessages.urls', namespace='messages')),
    url(r'^admin/', include(admin.site.urls)),
)

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)