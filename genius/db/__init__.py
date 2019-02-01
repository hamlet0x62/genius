from .model import *


def init_db(app):
    db.init_app(app)
    debug = app.config['DEBUG']
    if not debug:
        with app.app_context():
            db.drop_all()
            db.create_all()