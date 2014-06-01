# -*- coding: utf-8 -*-

from __future__ import absolute_import

import autocomplete_light

autocomplete_light.autodiscover()

from django.contrib.auth.decorators import login_required
from userena.contrib.umessages import views as messages_views
from django.conf.urls import patterns, url

from django.contrib import admin

from .forms import MessageForm


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^compose/$',
        messages_views.message_compose, {'compose_form': MessageForm},
        name='userena_umessages_compose'),

    url(r'^$',
        login_required(messages_views.MessageListView.as_view(
            paginate_by=None,
        )),
        name='userena_umessages_list'),

    url(r'^view/(?P<username>[\.\w]+)/$',
        login_required(messages_views.MessageDetailListView.as_view(
            paginate_by=None,
            extra_context={'form': MessageForm()}
        )),
        name='userena_umessages_detail'),

)
