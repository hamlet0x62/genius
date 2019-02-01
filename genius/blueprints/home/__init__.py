from .view import home_bp


def init_app(app):
    app.register_blueprint(home_bp)
    print(home_bp.template_folder)