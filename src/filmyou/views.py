from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from pylucene.search import MovieReader

footer = "UDC"

def home(request):
    """
    Renders homepage
    """
    if request.user.is_authenticated():
        template = 'main.html'
    else:
        template = 'intro.html'

    return render_to_response(template, {},
        context_instance=RequestContext(request))


def profile(request, username):
    """
    Renders page for user profiles
    """
    user = User.objects.get(username__exact=username)

    c = {'user': user}

    return render_to_response('profile.html', c,
        context_instance=RequestContext(request))


def search(request, template='results.html', page_template='page_results.html',
    extra_context=None):
    """
    Renders search page
    """
    if request.is_ajax():
        return _search_ajax(request, page_template)

    query = request.POST.get('query', None)
    if query:
        reader = MovieReader()
        results = reader.query('title', query)
    else:
        results = []

    c = {
        'page_template': page_template,
        'query': query,
        'results': results
    }

    if extra_context is not None:
        c.update(extra_context)
    return render_to_response(template, c,
        context_instance=RequestContext(request))


def _search_ajax(request, template):
    last_id = request.GET['last_id']
    last_score = request.GET['last_score']
    query = request.GET['query']
    reader = MovieReader()
    results = reader.search_after("title", query, last_id, last_score)

    c = {
        'query': query,
        'results': results
    }

    return render_to_response(template, c,
        context_instance=RequestContext(request))


def advanced_search(request):
    """
    Renders advanced search settings page
    """
    if request.POST:
        c = {
            'page_template': 'page_results.html'
        }
        return render_to_response('results.html', c,
        context_instance=RequestContext(request))

    template = 'advanced_search.html'
    c = {
        'fields': [
            _("title"),
            _("genre"),
            _("director"),
            _("cast"),
            _("writer"),
            _("year"),
            _("runtime"),
            _("...")
        ]
    }

    return render_to_response(template, c,
        context_instance=RequestContext(request))

    # query = request.POST.get('query', None)
    # if query:
    #     reader = MovieReader()
    #     results = reader.query('title', query)
    # else:
    #     results = []

    # c = {
    #     'page_template': page_template,
    #     'query': query,
    #     'results': results
    # }

    # if extra_context is not None:
    #     c.update(extra_context)
    # return render_to_response(template, c,
    #     context_instance=RequestContext(request))


def movie(request, movie_id):
    """
    Renders homepage
    """
    reader = MovieReader()
    results = reader.query('id', movie_id)

    if results:
        movie = results[0]
    else:
        raise Http404

    c = { 'movie': movie }

    return render_to_response('movie.html', c,
        context_instance=RequestContext(request))


def recommendations(request):
    """
    Renders homepage
    """
    raise Http404


def friends(request):
    """
    Renders homepage
    """
    raise Http404
