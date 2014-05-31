# -*- coding: utf-8 -*-

import urllib

from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def navactive(request, urls, *args):
    """
    Custom template tag for active links in sidebar.
    :param request: request object
    :param urls: current url
    :param *args: urls arguments
    :return: "active" or ""
    """
    if request.path in (reverse(url, args=args) for url in urls.split()):
        return "active"
    return ""


@register.simple_tag
def query_without(query, field, text):
    """
    Custom template tag for making queries removing a field.
    :param query: original query (list of 2-tuples)
    :param field: field to remove
    :param text: content of the field
    :return: url to new query
    """
    new_query = []
    for (f, t) in query:
        if f != field:
            if f == 'year':
                start, end = t.split(",")
                new_query.append(('year_start', start))
                new_query.append(('year_end', end))
            else:
                new_query.append((f, t))

    if new_query:
        return reverse('films:search') + '?' + urllib.urlencode(new_query)
    else:
        return reverse('films:advanced_search')
