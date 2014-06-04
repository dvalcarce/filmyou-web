# !/usr/bin/env python2

# -*- coding: utf-8 -*-
import sys

from django.contrib.auth.models import User
from userena.models import UserenaSignup
from userena import settings as userena_settings

"""
This script will create Netflix users on Django.
Default password is '1234'.

Instructions:
    $ python manage.py shell
    >>> import sys
    >>> sys.argv = ['users_django.py', 'path_to_ratings_file']
    >>> execfile('path_to_this_script')

"""

if __name__ == '__builtin__':
    if len(sys.argv) < 2:
        print "{0} <ratings>".format(sys.argv[0])
        sys.exit(0)

    print "Reading ratings"
    with open(sys.argv[1], 'r') as data:
        users = set([])
        for line in data:
            user, film, score = line[:-1].split(",")
            users.add(int(user))

    print "Creating", len(users), "users"
    for u in users:
        new_user = UserenaSignup.objects.create_user(
            username=u,
            email='filmyou_user_' + str(u) + '@irlab.org',
            password='1234',
            active=True,
            send_email=False)

