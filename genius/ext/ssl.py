from flask_sslify import SSLify


def init_app(app):
    SSLify(app)
