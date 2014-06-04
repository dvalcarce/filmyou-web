# -*- coding: utf-8 -*-

from __future__ import absolute_import


def _retrieve_int(querydict, key):
    """
    Retrieve an int from a dict or None
    :param querydict: query dictionary
    :param key: key to retrieve
    :return: integer or None
    """
    try:
        return int(querydict.pop(key)[0])
    except ValueError or KeyError:
        return None


def _clean(text, removable_chars=u"+-&|!(){}[]^\"~*?:\\"):
    table = {ord(char): None for char in removable_chars}
    return text.translate(table)


def sanitize(text):
    """
    Sanitize text for Lucene
    :param text: text
    :return: sanitized text
    """
    if text:
        return _clean(text.lower().strip()).encode("utf-8")
    raise ValueError


valid_fields = {
    'title',
    'genre',
    'language',
    'country',
    'director',
    'writer',
    'cast',
    'year_start',
    'year_end'
}


def check_field(field):
    """
    Check if the given field is valid
    :param field: field
    :return: field or KeyError
    """
    sanitized_field = sanitize(field)
    if sanitized_field in valid_fields:
        return sanitized_field
    raise KeyError(field + " is not a valid field")


def prepare_query(request):
    """
    Parse GET parameters to generate a query for Lucene
    :param request: request object
    :return: [(field1, text1), (field2, text2), ...]
    """
    # Get a mutable copy of GET parameters
    query = request.GET.copy()

    # Remove pagination parameters
    query.pop('last_id', None)
    query.pop('last_score', None)

    # Manage search bar parameters
    if 'query' in query:
        for term in query.pop('query'):
            try:
                idx = term.index(":")
                field = check_field(term[:idx])
                text = term[idx + 1:].strip()
                query.appendlist(field, sanitize(text))
            except (KeyError, ValueError):
                # Invalid field, treat as a title search
                query.appendlist('title', sanitize(term))

    # Transform year_start and year_end parameters into year parameter
    if 'year_start' in query or 'year_end' in query:
        year_start = _retrieve_int(query, 'year_start')
        year_end = _retrieve_int(query, 'year_end')

        if year_start or year_end:
            year_start = "0" if year_start is None else year_start
            year_end = "50000" if year_end is None else year_end
            query['year'] = "{0},{1}".format(year_start, year_end)

    # Manage autocompletion parameters
    ending = "-autocomplete"
    d = []
    for (k, values) in query.lists():
        if k.endswith(ending):
            try:
                k = check_field(k[:k.rindex(ending)])
            except KeyError:
                # Invalid field
                continue

        for v in values:
            try:
                d.append((k, sanitize(v)))
            except ValueError:
                # Invalid text
                continue

    return d
