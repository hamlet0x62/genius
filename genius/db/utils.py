from .base import db


def save_all(models):
    db.session.add_all(models)
    db.session.commit()

