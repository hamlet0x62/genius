from flask import request, abort

from http import HTTPStatus

from functools import partial


def id_required_route(bp, id_label):
    """
    registering 2 route functions,
    one registered `'/' + f.__name__` route and `f.__name__ + '_index'` endpoint
    the other one  registered `/f.__name__/<int:#id_label>` and `f.__name__` endpoint

    this decorator make view functions able to fetch an id from both #request.view_args
     and #request.args
    Example:
    @id_required('user_id')
    def profile(user_id):
        user_profile = db.get_user_profile(user_id)
        return user_profile

    :param id_label: the prop name to access the id value
    :param bp: the blueprint
    :return:
    """
    def outer(f):
        @bp.route(f'/{f.__name__}', endpoint=f'{f.__name__}_index')
        def index(*args, **kws):
            id_val = request.args.get(id_label, None)
            if not id_val:
                abort(HTTPStatus.NOT_FOUND)
            return f(id_val, *args, **kws)

        @bp.route(f'/{f.__name__}/<int:{id_label}>', endpoint=f'{f.__name__}')
        def with_view_args(*args, **kws):
            if request.view_args.get(id_label, None):
                return f(*args, **kws)
            abort(HTTPStatus.NOT_FOUND)
    return outer


def gen_bp_id_rquired(bp):
    """
    generate id required view route for blueprints
    :param bp:
    :return:
    """
    return partial(id_required_route, bp)

