from functools import partial

from flask import current_app, abort, jsonify
from flask_login import current_user

from genius.db.model import UsersLendBook, BookOfUser, User, UserCollection

from genius.util.schemas import table_header_dict as base_header_dict, userlendbook_schema, \
    bookofuser_schema, user_schema, user_collection_schema, user_collection_header_patch


from functools import wraps


def jsonify_objs(cls, objs, schema=None):
    return {
        'data': list(map(lambda x: x.to_dict(schema=schema), objs))
    }


_empty_dict = {}


def get_table_headers(cls, header_patch=_empty_dict):
    """
    :param cls, header_patch:
    :return: dict with key: prop, label
    """

    return {
        prop: header_patch.get(prop, None) or base_header_dict.get(prop)
        for prop in cls.__repr_attrs__ if any((
        header_patch.get(prop, None), base_header_dict.get(prop, None)
        ))
    }


def user_logined():
    return current_user.is_authenticated or current_app.login_manager._login_disabled


wrap_userlendbooks = partial(jsonify_objs, UsersLendBook, schema=userlendbook_schema)
wrap_bookofusers = partial(jsonify_objs, BookOfUser, schema=bookofuser_schema)
wrap_users = partial(jsonify_objs, User, schema=user_schema)
wrap_usercollections = partial(jsonify_objs, UserCollection, schema=user_collection_schema)

userlendbook_headers = get_table_headers(UsersLendBook)
bookofusers_headers = get_table_headers(BookOfUser)
usercollection_headers = get_table_headers(UserCollection, header_patch=user_collection_header_patch)


# json serialize tools
def jsonify_result(f, wrap_func=None):
    @wraps(f)
    def wrapper(*args, **kws):
        rst = f(*args, **kws)

        if rst and wrap_func:
            return jsonify(
                wrap_func(rst)
            )
        abort(404)

    return wrapper
# jsonify collections decorator for view functions
jsonify_userlendbook = partial(jsonify_result, wrap_func=wrap_userlendbooks)
jsonify_bookofuser = partial(jsonify_result, wrap_func=wrap_bookofusers)
jsonify_user = partial(jsonify_result, wrap_func=wrap_users)
jsonify_usercollection = partial(jsonify_result, wrap_func=wrap_usercollections)