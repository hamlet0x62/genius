from genius.blueprints import home, book, user
from flask import g


def init_app(app):
    home.init_app(app)
    book.init_app(app)
    user.init_app(app)
    for name, bp in app.blueprints.items():
        @bp.before_request
        def register_tabs():
            g.index = name
