from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from pages.models import Document
from pages.forms import DocumentForm

import json


def home(request):
    """
    Renders homepage
    """
    c = {'title': "Homepage", 'footer': footer, 'request': request}

    return render_to_response('home.html', c, context_instance=RequestContext(request))
