# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.views.generic import View
from django.shortcuts import render


class HomeView(View):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            template = 'home.html'
        else:
            template = 'intro.html'

        return render(request, template)


