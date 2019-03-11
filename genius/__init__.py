from flask import Flask, request, make_response, render_template

from flask_login import logout_user

from werkzeug.datastructures import ImmutableDict
from werkzeug.wsgi import SharedDataMiddleware
from genius import db, ext, blueprints as bp
from genius.db import User, BookOfUser, Branch, Book, School, Category, \
    LendLimitation, Role, UsersLendBook, CommonAddress
from genius.db.file_model import BookThumbnail, BookDetailImage
from genius.global_settings import UPLOAD_DIR, STATIC_FILE_DIR
import click
import os


def create_app(config=None):
    """
    >>> app = create_app()
    2018...
    """
    app = Flask(__name__)
    if config is None:
        mode = os.environ.get("GENIUS_MODE")
        config_file = 'config.py'
        if mode == 'deploy':
            config_file = 'deploy_config.py'
        app.config.from_pyfile(config_file)
        jinja_config = {k[3:].lower(): v for k, v in app.config.items() if k.lower().startswith('j2_')}
        jinja_config.update(app.jinja_options)
        app.jinja_options = ImmutableDict(**jinja_config)

    configure_app(app)
    db.init_db(app)
    bp.init_app(app)

    # register plugins finally
    ext.init_app(app)

    @app.route('/jerry_lend_books')
    def _():
        jerry = User.query.first()
        simon = User.query.filter_by(User.id != jerry.id)
        book = Book.query.first()
        jerry.post_book(book)
        b_copy = BookOfUser.query.first()
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
        test_school = School.create_or_get(addr="Nanchang.Jiangxi",
                                           name="JEFU", tel="8380000")

        from genius.db.util_model import user_address
        address_item = user_address(label='Home', common_addr=CommonAddress(code='100000'), detail='NB534')

        lend_limitation = LendLimitation.create_or_get(limit_days=30, limit_nums=10)
        from genius.global_settings import BRANCH_OPERATION_ROlE, OL_OPERATION_ROLE, USER_ROLE
        roles = [Role.create_or_get(description=role_name, limit_type_id=lend_limitation.id)
                 for role_name in (BRANCH_OPERATION_ROlE, OL_OPERATION_ROLE, USER_ROLE)]
        branch = Branch.create_or_get(name="Disney Land",
                                      school=test_school,
                                      addr=test_school.addr + "NB534",
                                      tel=test_school.tel)
        c = Category.create_or_get(category_name="Fictions")
        b = Book.create_or_get(name="A Tale of 2 cities", authors=["Charles Dickens"],
                               isbn="I372.2", categories=[c])

        simon = User.create_or_get(username="itsimon",
                                   nickname="Simon",email="i@aboutsimond.me",
                                   role=roles[1], password='pass', school=test_school)
        jerry = User.create_or_get(username="itsjerry", nickname="Jerry", email="i@jry.me",
                                   role=roles[-1], password='pass', school=test_school)
        simon.address_items.append(address_item)
        simon.save()
        print(simon.address_items)
        *_, item = simon.address
        user_book = jerry.post_book(b, address_id=item.id)

        user_lend_book = simon.lend_book(user_book, branch)
        simon.ensure_lending([user_lend_book])

    @app.cli.command('display')
    def display_user():
        display_list = [('users', User), ('books', Book),
                        ('userbooks', BookOfUser), ('', UsersLendBook),
                        ('', Role), ]
        for abbr, cls in display_list:
            abbr = abbr or cls.__tablename__
            click.echo('{:*^30}'.format(abbr))
            for obj in cls.query.all():
                click.echo(repr(obj))


def configure_app(app: Flask):
    ...

app = create_app()

