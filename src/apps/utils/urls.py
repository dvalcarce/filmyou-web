# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf.urls import patterns, url

from .forms import EditProfileFormExtra


urlpatterns = patterns(
    '',
    url(
        r'^accounts/(?P<username>[\.\w-]+)/edit/$',
        'userena.views.profile_edit',
        {'edit_profile_form': EditProfileFormExtra},
        name='edit-profile'),
)
