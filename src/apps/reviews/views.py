from os import path

from braces.views import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import View, CreateView, DeleteView

from apps.films.models import Film
from apps.reviews.forms import ReviewForm
from apps.reviews.models import Review

app_name = Review._meta.app_label


class Reviews(LoginRequiredMixin, View):
    template_name = path.join(app_name, "review_list.html")
    page_template = path.join(app_name, "review_page.html")

    def _get_next(self, page):
        return reverse('reviews:list') + '?page=' + str(int(page) + 1)


    def _get_preferences(self, reviews):
        films = set()
        for review in reviews:
            films.add(review.film)
        self.request.user.profile.get_preferences_for_films(films)

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            return self._reviews_ajax()

        page = self.request.GET.get('page', 1)

        all_reviews = self.request.user.profile.review_set.all().prefetch_related("film")
        paginator = Paginator(all_reviews, 12)
        try:
            reviews = paginator.page(page)
        except:
            reviews = []

        self._get_preferences(reviews)

        c = {
            'page_template': self.page_template,
            'reviews': reviews,
            'next': self._get_next(page),
            'title': _("My reviews")
        }

        return render(self.request, self.template_name, c)

    def _reviews_ajax(self, page):
        try:
            page = int(self.request.GET.get('page'))
        except:
            return HttpResponse()

        all_reviews = self.request.user.profile.review_set.all().prefetch_related("film")
        paginator = Paginator(all_reviews, 12)
        try:
            reviews = paginator.page(page)
        except:
            return HttpResponse()

        if reviews:
            self._get_preferences(reviews)

            c = {
                'reviews': reviews,
                'next': self._get_next(page),
            }

            return render(self.request, self.page_template, c)
        else:
            return HttpResponse()


class CreateReview(LoginRequiredMixin, CreateView):
    """Creates a Review for a Film"""
    model = Review
    form_class = ReviewForm

    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        form.instance.film = get_object_or_404(Film, pk=int(self.kwargs['pk']))
        return super(CreateReview, self).form_valid(form)


class RemoveReview(LoginRequiredMixin, DeleteView):
    """Delete a Review"""
    model = Review

    def get_success_url(self):
        return self.film.get_absolute_url()

    def get_object(self, queryset=None):
        obj = super(RemoveReview, self).get_object()
        if not obj.author == self.request.user.profile:
            raise PermissionDenied()
        self.film = obj.film
        return obj