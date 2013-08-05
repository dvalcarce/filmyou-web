from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'filmyou.views.home', name='home'),
    # url(r'^filmyou/', include('filmyou.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^movie/(?P<movie_id>[0-9]+)/$', 'filmyou.views.movie'),
    url(r'^profile/(?P<username>[0-9A-Za-z]+)/$', 'filmyou.views.profile'),

   # Login
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/', include('registration.backends.simple.urls')),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name' : 'registration/password_reset.html',  'post_reset_redirect': '/logout/' }),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
