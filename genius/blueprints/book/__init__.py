from .view import book_bp


def init_app(app):
    app.register_blueprint(book_bp)