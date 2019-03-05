from flask_cors import CORS, cross_origin

cors = CORS()
_cors_resources = []


def configure_bp(app):
    for bp in filter(lambda blueprint: getattr(blueprint, 'cors', None), app.blueprints):
        if isinstance(bp.url_pattern, list):
            _cors_resources.extend(bp.url_pattern)
        else:
            _cors_resources.append(bp.url_pattern)


def init_app(app):
    configure_bp(app)
    cors.init_app(app, resource=_cors_resources)
