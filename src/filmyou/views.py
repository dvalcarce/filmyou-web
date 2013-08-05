from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from django.contrib.auth.models import User

from pylucene.search import MovieReader

from datetime import datetime

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

def movie(request, movie_id):
    """
    Renders homepage
    """
    reader = MovieReader()
    results = reader.query("id", movie_id)

    if results:
        movie = results[0]
    else:
        raise Http404

    title = reader.get_fields(movie, "title")[0]
    year = reader.get_fields(movie, "year", numeric=True)[0]
    genre = reader.get_fields(movie, "genre")
    runtime = reader.get_fields(movie, "runtime")[0]
    rating = reader.get_fields(movie, "rating")[0]
    director = reader.get_fields(movie, "director")
    writer = reader.get_fields(movie, "writer")
    cast = reader.get_fields(movie, "cast")
    ts = reader.get_fields(movie, "released", numeric=True)[0].longValue()
    if ts == -2**63:
        released = None
    else:
        released = datetime.fromtimestamp(ts)
    plot = reader.get_fields(movie, "plot")[0]
    fullplot = reader.get_fields(movie, "fullplot")[0]
    poster = reader.get_fields(movie, "poster")[0]

    c = {
        'movie_id': movie_id,
        'title': title,
        'year': year,
        'genre' : genre,
        'runtime' : runtime,
        'rating' : rating,
        'director' : director,
        'writer' : writer,
        'cast' : cast,
        'released' : released,
        'plot' : plot,
        'fullplot' : fullplot,
        'poster': poster
    }

    return render_to_response('movie.html', c, context_instance=RequestContext(request))
