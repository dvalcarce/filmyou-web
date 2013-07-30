from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.models import User


footer = "UDC"

def home(request):
    """
    Renders homepage
    """
    c = {}

    return render_to_response('main.html', c, context_instance=RequestContext(request))

def profile(request, username):
    """
    Renders homepage
    """
    user = User.objects.get(username__exact=username)

    c = {'user': user}

    return render_to_response('profile.html', c, context_instance=RequestContext(request))
