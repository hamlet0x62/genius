from .principal import principal
from .login_manager import login_manager

import genius.ext.cors
import genius.ext.ssl


def init_app(app):
    principal.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app)

