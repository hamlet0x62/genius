from .views import user_bp
from .apis import user_api_bp

from .settings import tabs as aside_nav_tabs


def render_globals():
    return {
        'ASIDE_NAVS':  aside_nav_tabs
    }


def init_app(app):
    bps = [user_bp, user_api_bp]

    for bp in bps:
        bp.context_processor(render_globals)
        app.register_blueprint(bp)
