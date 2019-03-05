from flask import request, abort, g

from collections import namedtuple

from functools import wraps

from typing import Iterable

import json


from genius.util.http import api_abort

bookofuser_form_schema = {
    'book_id': lambda x: int(x),
    'user_id': lambda x: int(x),
    'deprecation': lambda x: int(float(x) * 100),  # store an integer equal to 100 x real deprecation rate
}


bookofuser_form = namedtuple('BookOfUserForm', bookofuser_form_schema.keys())

no_marshal = object()


def recurse_int(int_arr):
    return [recurse_int(item) if isinstance(item, Iterable) else int(item) for item in int_arr]


new_genius_form_schema = {
    'isbn': no_marshal,
    'deprecation': lambda x: int(float(x) * 100) ,
    'description': no_marshal,
    'photoIds': no_marshal,
    'addressId': int,
}

new_genius_form = namedtuple('NewGeniusForm', new_genius_form_schema.keys())


def fill_form(form_schema, form_tuple):
    """
    process json type request
    parse json data into g.data_dict if exists
    :param form_schema:
    :param form_tuple:
    :return:
    """
    def outer(f):
        @wraps(f)
        def wrapper(*args, **kws):
            filled_dict = {}
            data_dict = json.loads(request.data)
            for k, marshal in form_schema.items():
                if data_dict.get(k, None):
                    val = data_dict[k]
                    val = marshal(val) if callable(marshal) else val if marshal is no_marshal else marshal

                    filled_dict.setdefault(k, val)
                else:
                    return api_abort(400, message=f'{k.capitalize()} field required.')
            g.data_dict = data_dict
            return f(*args, form=form_tuple(**filled_dict), **kws)
        return wrapper
    return outer
