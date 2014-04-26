#!/usr/bin/env python2

import sys

from django.contrib.auth.models import User

import names


"""
This script will create Netflix users on Django.
Default password is '1234'.

Instructions:
    $ python manage.py shell
    >>> import sys
    >>> sys.argv = ['path_to_ratings_file']
    >>> execfile('path_to_this_script')

"""
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "{0} <ratings>".format(sys.argv[0])
        sys.exit(0)

    with open(sys.argv[1], 'r') as data:
        users = set([])
        for line in data:
            user, film, score = line[:-1].split(",")
            users.add(int(user))

    for u in user:
        user = User(
            first_name=unicode(names.get_first_name()),
            last_name=unicode(names.get_last_name()),
            id=unicode(u),
            username=u'user%d' % u,
            password=u'pbkdf2_sha256$10000$MekzC5PQ58x2$3C5TLXHec3X4Ihd7vWFZHYM4Uf3PPvqfVfi5k0TeERM=',
            is_active=True)
        data.append(user)

User.objects.bulk_create(users)
