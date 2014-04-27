# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


@login_required
def details(request, username):
    """
    Renders the user profile page
    :param request: request object
    :param username: user name
    :return: template
    """
    if request.user.username != username:
        raise PermissionDenied
    try:
        user = User.objects.get(username__exact=username)
    except User.DoesNotExist:
        raise Http404

    c = {'user': user}

    return render_to_response('profile.html', c, context_instance=RequestContext(request))
