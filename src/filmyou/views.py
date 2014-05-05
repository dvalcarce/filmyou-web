# -*- coding: utf-8 -*-

from __future__ import absolute_import

from os import path

from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin


class HomeView(TemplateView):
    template_name = 'intro.html'


class UserDetails(LoginRequiredMixin, TemplateView):
    template_name = path.join('users', 'user_detail.html')
