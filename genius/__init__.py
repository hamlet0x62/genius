from flask import Flask, request, make_response, render_template
from werkzeug.datastructures import ImmutableDict
from werkzeug.wsgi import SharedDataMiddleware
import genius.blueprints as bp
from genius import db
from genius.db import User, BooksOfUser, Branch, Book, School, Category, LendLimitation, Role
from genius.db.file_model import BookThumbnail, BookDetailImage
from genius.global_setting import UPLOAD_DIR, STATIC_FILE_DIR
import click


def create_app(config=None):
    """
    >>> app = create_app()
    2018...
    """
    app = Flask(__name__)
    if config is None:
        app.config.from_pyfile('config.py')
        jinja_config = {k[3:].lower(): v for k, v in app.config.items() if k.lower().startswith('j2_')}
        jinja_config.update(app.jinja_options)
        app.jinja_options = ImmutableDict(**jinja_config)
    db.init_db(app)
    bp.init_app(app)

    @app.route('/jerry_lend_books')
    def _():
        jerry = User.query.first()
        simon = User.query.filter_by(User.id != jerry.id)
        book = Book.query.first()
        jerry.post_book(book)
        b_copy = BooksOfUser.query.first()
        branch = Branch.query.first()
        rec = jerry.lend_book(branch=branch, book_copy=b_copy)

        if not rec:
            return make_response("Not Permitted..")

        return make_response(repr(rec).strip())
    app.wsgi_app = SharedDataMiddleware(
        app.wsgi_app, {
            '/i': UPLOAD_DIR,
            '/static': STATIC_FILE_DIR
        }
    )

    add_cli_interfaces(app)
    return app


def add_cli_interfaces(app):
    @app.cli.command()
    def flushdb():
        database = db.db
        database.drop_all()
        database.create_all()

    @app.cli.command('add-models')
    def add_models():
        database = db.db
        database.drop_all()
        database.create_all()
        test_school = School.create_or_get(school_addr="Nanchang.Jiangxi",
                                           school_name="JEFU", school_tel="8380000")

        lend_limitation = LendLimitation.create_or_get(limit_days=30, limit_nums=10)
        default_r = Role.create_or_get(role_name="Normal", limit_type_id=lend_limitation.id)
        branch = Branch.create_or_get(branch_name="Disney Land",
                                      school=test_school,
                                      branch_addr=test_school.school_addr + "NB534",
                                      branch_tel=test_school.school_tel)
        c = Category.create_or_get(category_name="Fictions")
        b = Book.create_or_get(name="A Tale of 2 cities", author="Charles Dikens",
                               isbn="I372.2", categories=[c])
        ''.strip()

        simon = User.create_or_get(username="itsimon", email="i@aboutsimond.me", role=default_r)
        jerry = User.create_or_get(username="itsjerry", nickname="Jerry", email="i@jry.me", role=default_r)
