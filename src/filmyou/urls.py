from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'filmyou.views.home', name='home'),
    # url(r'^filmyou/', include('filmyou.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # Login
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/', include('registration.backends.simple.urls')),
)
