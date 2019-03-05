from flask import render_template, make_response, url_for, redirect, current_app, request, session
from flask import blueprints as bp
from flask_login import current_user, login_user, logout_user, login_required
from flask_principal import identity_changed, identity_loaded, AnonymousIdentity, Identity

from functools import wraps

from genius.db.model import Book, User
from genius.global_settings import NAV_TABS
from genius.util.form_util import render_form

from .forms import LoginForm
from .errors import FormNotMatchException

home_bp = bp.Blueprint('home', __name__, url_prefix='/')


@home_bp.route('/')
def send_home():
    books = (Book.newly_books(), Book.most_copies(), Book.most_copies())
    rank_types = (u'新书速递', u'畅销', u'最受关注')
    book_rank_map = {rank_type: target_books for rank_type, target_books in zip(rank_types, books)}
    return render_template('index.j2', book_rank_map=book_rank_map)


@home_bp.route('/login', methods=['POST', 'GET'])
@render_form(LoginForm, 'login.j2')
def login(form: LoginForm):
    user = form.match_db()  # will throws FormNotMatchException if not match
    login_user(user)
    identity = Identity(user.id)
    identity_changed.send(current_app._get_current_object(), identity=identity)
    return make_response(repr(request.args))


@home_bp.route('/logout')
def logout():
    logout_user()
    for k in ('identity.name', 'identity.auth_type'):
        session.pop(k, None)
    identity_changed.send(current_app, identity=AnonymousIdentity())
    return redirect(url_for('.send_home'))


@home_bp.app_context_processor
def nav_tabs():
    return {'NAV_TABS': NAV_TABS}
