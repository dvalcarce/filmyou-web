# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.db import models


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-managed "created" field.
    """
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-created',)
