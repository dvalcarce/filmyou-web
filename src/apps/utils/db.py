# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.http import Http404


def retrieve_in_order_from_db(model, ids, prefetch=True):
    """
    Retrieve entities of the given model from the RDBMS in order given their ids.
    :param model: model of the entities
    :param ids: ids of the entities
    :param prefetch: prefetch many-to-many relationships
    :return: a list of entities
    """
    # Prefetch related
    if prefetch:
        relationships = [m2m.attname for m2m in model._meta._many_to_many()]
        entities = model.objects.all().prefetch_related(*relationships).in_bulk(ids)
    else:
        entities = model.objects.in_bulk(ids)

    # Order by search order
    ordered_entities = [entities.get(id, None) for id in ids]

    # Filter not found entities
    filtered_entities = filter(None, ordered_entities)

    return filtered_entities


def retrieve_with_related_or_404(model, id):
    """
    Retrieve an object from DB with prefetch related or raise 404 error
    :param model: model
    :param id: pk
    :return: object
    """
    relationships = [m2m.attname for m2m in model._meta._many_to_many()]

    try:
        object = model.objects.all().prefetch_related(*relationships).get(pk=id)
    except model.DoesNotExist:
        raise Http404()

    return object
