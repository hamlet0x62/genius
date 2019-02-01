from flask import request, current_app, render_template
from flask import blueprints as bp
from genius.db.model import Book
from genius.global_setting import NAV_TABS

home_bp = bp.Blueprint('home', __name__, url_prefix='/')


@home_bp.route('/')
def send_home():
    books = Book.newly_books() * 5
    rank_types = (u'新书速递', u'畅销', u'最受关注')
    book_rank_map = {rank_type: books for rank_type in rank_types}
    return render_template('index.j2', book_rank_map=book_rank_map)


@home_bp.app_context_processor
def nav_tabs():
    return {'NAV_TABS': NAV_TABS}
