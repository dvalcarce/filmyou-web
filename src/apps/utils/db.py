# -*- coding: utf-8 -*-

from __future__ import absolute_import


def retrieve_in_order_from_db(model, ids):
    """
    Retrieve entities of the given model from the RDBMS in order given their ids.
    :param model: model of the entities
    :param ids: ids of the entities
    :return: a list of entities
    """
    # Retrieve from RDBMS
    entities = model.objects.in_bulk(ids)

    #TODO: prefetch_related

    # Order by search order
    ordered_entities = [entities.get(id, None) for id in ids]

    # Filter not found entities
    filtered_entities = filter(None, ordered_entities)

    return filtered_entities
