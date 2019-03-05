from .view import book_bp
from .apis import book_api


def init_app(app):
    app.register_blueprint(book_bp)
    app.register_blueprint(book_api)

