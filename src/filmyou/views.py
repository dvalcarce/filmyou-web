# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.views.generic import View
from django.shortcuts import render

from apps.films.views import render_homepage


class HomeView(View):
    template_name = 'intro.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return render_homepage(request)
        else:
            return render(request, self.template_name)


