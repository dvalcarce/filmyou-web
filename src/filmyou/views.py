from django.shortcuts import render_to_response
from django.template import RequestContext


footer = "UDC"

def home(request):
    """
    Renders homepage
    """
    c = {'title': "FilmYou", 'footer': footer, 'request': request}

    return render_to_response('main.html', c, context_instance=RequestContext(request))

