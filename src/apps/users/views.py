from __future__ import absolute_import

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


@login_required
def details(request, username):
    """
    Renders page for user profiles
    """
    user = User.objects.get(username__exact=username)

    c = {'user': user}

    return render_to_response('profile.html', c,
                              context_instance=RequestContext(request))
