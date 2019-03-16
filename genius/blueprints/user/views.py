from flask import Blueprint, render_template, abort, redirect, request, url_for

from functools import wraps, partial

from genius.util.view_util import id_required_route
from genius.db.model import User

from genius.util.serialize import bookofusers_headers, userlendbook_headers, usercollection_headers, user_logined

user_bp = Blueprint('user', __name__, url_prefix='/user', template_folder='templates')

user_bp_id_required = partial(id_required_route, user_bp)


def render_template_with_headers(template_name, headers, exception_code=404):
    def outer(f):
        """
        :param f: return dict type result, for rendering templates
        :return:
        """
        @wraps(f)
        def wrapper(*args, **kws):
            rst = f(*args, **kws)
            if rst:
                return render_template(template_name, headers=headers, **rst)
            abort(exception_code)
        return wrapper
    return outer


def render_daterange(daterange_prop, daterange_label):
    def outer(f):
        @wraps(f)
        def wrapper(*args, **kws):
            rst = f(*args, **kws)
            if rst:
                rst.update(daterange_prop=daterange_prop, daterange_label=daterange_label)
                return rst
            return rst
        return wrapper
    return outer


left_date_daterange = render_daterange(daterange_prop='left_date', daterange_label=u'借阅日期')
create_at_daterange = render_daterange(daterange_prop='create_at', daterange_label=u'创建日期')


@user_bp.route('/space')
def space():
    return render_template('user_space.j2', headers=userlendbook_headers)


@user_bp.route('/update_profile')
def update_profile():
    return render_template('update_profile.j2')


@user_bp.route('/borrowing')
@render_template_with_headers('user_base.j2', userlendbook_headers)
@left_date_daterange
def borrowing():
    return {
        'request_url': url_for('user_api.borrowing'),
    }


@user_bp.route('/borrow_history')
@render_template_with_headers('user_base.j2', userlendbook_headers)
@left_date_daterange
def borrow_history():
    return {
        'request_url': url_for('user_api.borrow_history'),
    }


@user_bp.route('/lending_genius')
@render_template_with_headers('user_base.j2', bookofusers_headers)
def lending_genius():
    return {
        'request_url': url_for('user_api.lending_genius')
    }


@user_bp.route('/blocking_genius')
@render_template_with_headers('user_base.j2', bookofusers_headers)
def blocking_genius():
    return {
        'request_url': url_for('user_api.blocking_genius')
    }


@user_bp.route('/asleep_genius')
@render_template_with_headers('user_base.j2', bookofusers_headers)
def asleep_genius():

    return {
        'request_url': url_for('user_api.asleep_genius')
    }


@user_bp.route('/new_genius')
def new_genius():
    return render_template('new_genius.j2')


@user_bp_id_required('user_id')
def profile(user_id):
    rst = User.query.get_or_404(user_id)

    return render_template('user_profile.j2', user=rst)


@user_bp.route('/collection')
@render_template_with_headers('user_base.j2', usercollection_headers)
def collection():
    return {
        'request_url': url_for('user_api.collected_book')
    }


@user_bp.before_request
def authenticate():
    if not user_logined():
        return redirect(url_for('home.login', n=request.url))


