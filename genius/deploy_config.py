DEBUG = 1
SECRET_KEY = "GeNiuS"
DB_NAME = "genius"
DB_USER = "ondev"
DB_PASSWORD = "password"
LOGIN_DISABLED = 0
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://ondev:{DB_PASSWORD}@localhost:3306/{DB_NAME}"
SQLALCHEMY_ECHO = 0
# Jinja configurationss
TEMPLATES_AUTO_RELOAD = 1
J2_LINE_STATEMENT_PREFIX = '#'

SSL_ENABLED = 0

# deploy host setting
DEPLOY_HOST = 'genius.aboutsimond.me'