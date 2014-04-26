from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.simple_tag
def navactive(request, urls, *args):
    """
    Custom template tag for active links in sidebar.
    """
    if request.path in (reverse(url, args=args) for url in urls.split()):
        return "active"
    return ""
