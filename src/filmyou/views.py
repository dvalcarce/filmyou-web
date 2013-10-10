from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from pylucene.search import MovieReader

from filmyou.models import Movie
from filmyou.models import MyUser


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


@login_required
def profile(request, username):
    """
    Renders page for user profiles
    """
    user = User.objects.get(username__exact=username)

    c = {'user': user}

    return render_to_response('profile.html', c,
        context_instance=RequestContext(request))


@login_required
def search(request, template='search_results.html',
    page_template='page_search_results.html'):
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

    user = MyUser.objects.get(username=request.user.username)
    movies = user.get_rate_for_movies(results)

    c = {
        'page_template': page_template,
        'query': query,
        'results': movies
    }

    return render_to_response(template, c,
        context_instance=RequestContext(request))


def _search_ajax(request, template):
    last_id = request.GET['last_id']
    last_score = request.GET['last_score']
    query = request.GET['query']
    reader = MovieReader()

    results = reader.search_after("title", query, last_id, last_score)

    user = MyUser.objects.get(username=request.user.username)
    movies = user.get_rate_for_movies(results)

    c = {
        'query': query,
        'results': movies
    }

    return render_to_response(template, c,
        context_instance=RequestContext(request))


@login_required
def advanced_search(request):
    """
    Renders advanced search settings page
    """
    if request.POST:
        c = {
            'page_template': 'page_search_results.html'
        }
        return render_to_response('search_results.html', c,
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


@login_required
def rating(request):
    """
    Renders advanced search settings page
    """
    if request.is_ajax():
        movie_id = int(request.GET['movie'])
        score = float(request.GET['score'])

        user = MyUser.objects.get(username=request.user.username)
        movie = Movie.objects.get(movie_id=movie_id)
        movie.rate(user, score)

        return HttpResponse("ok!")
    else:
        raise PermissionDenied


@login_required
def movie(request, movie_id):
    """
    Renders homepage
    """
    try:
        movie = Movie.objects.get(movie_id=movie_id)
    except ObjectDoesNotExist:
        raise Http404("Movie does not exist!")

    user = MyUser.objects.get(username=request.user.username)
    recommendations = user.get_rate_for_movies([movie])
    print recommendations

    if recommendations:
        movie, score = recommendations[0]
    c = {
        'movie': movie,
        'score': score,
    }

    return render_to_response('movie.html', c,
        context_instance=RequestContext(request))


@login_required
def recommendations(request, template='rec_results.html',
    page_template='page_rec_results.html'):
    """
    Renders recommendations page
    """
    user = MyUser.objects.get(username=request.user.username)

    recommendations = user.get_recommendations()

    c = {
        'page_template': page_template,
        'results': recommendations,
    }

    return render_to_response(template, c,
        context_instance=RequestContext(request))


@login_required
def friends(request):
    """
    Renders homepage
    """
    raise Http404
