
import math

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from django.contrib.auth.models import User

from pylucene.search import MovieReader

footer = "UDC"

def home(request):
    """
    Renders homepage
    """
    if request.user.is_authenticated():
        template = "main.html"
    else:
        template = "intro.html"

    return render_to_response(template, {}, context_instance=RequestContext(request))


def profile(request, username):
    """
    Renders page for user profiles
    """
    user = User.objects.get(username__exact=username)

    c = {'user': user}

    return render_to_response('profile.html', c, context_instance=RequestContext(request))


def search(request):
    """
    Renders search page
    """

    if request.is_ajax():
        # Endless scroll
        template = page_template
        return render_to_response(template,context,context_instance=RequestContext(request))

    results_per_page = 10

    query = request.POST["query"]
    reader = MovieReader()
    results, totalHits = reader.query("title", query, n_results=results_per_page)
    n_pages = int(math.ceil(totalHits / float(results_per_page)))
    page = 1

    c = {
        'query': query,
        'results': results,
        'totalHits': totalHits,
        'range_pages': range(1, min(n_pages, 6)),
        'page': 1
    }

    return render_to_response('results.html', c, context_instance=RequestContext(request))


def movie(request, movie_id):
    """
    Renders homepage
    """
    reader = MovieReader()
    results, unused_totalHits = reader.query("id", movie_id)

    if results:
        movie = results[0]
    else:
        raise Http404

    c = { 'movie': movie }

    return render_to_response('movie.html', c, context_instance=RequestContext(request))
