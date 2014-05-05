# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views


admin.autodiscover()

registration_patterns = patterns(
    '',
    url(r'^password/change/$',
        auth_views.password_change,
        name='password_change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='password_change_done'),
    url(r'^password/reset/$',
        auth_views.password_reset,
        name='password_reset'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='password_reset_done'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    # url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
    #     'django.contrib.auth.views.password_reset_confirm',
    #     {'template_name': 'registration/password_reset.html',
    #      'post_reset_redirect': '/accounts/logout/'})
    url(r'', include('registration.backends.default.urls'))
)

user_patterns = patterns(
    '',
    url(
        regex=r'^profile$',
        view=views.UserDetails.as_view(),
        name='details'
    )
)

urlpatterns = patterns(
    '',
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^films/', include('apps.films.urls', namespace='films')),
    url(r'^users/', include(user_patterns, namespace='users')),
    url(r'^accounts/', include(registration_patterns, namespace='registration')),
    url(r'^admin/', include(admin.site.urls)),
)

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)