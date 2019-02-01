DEBUG = 1
SECRET_KEY = "GeNiuS"
DB_NAME = "genius"
DB_USER = "nor"
DB_PASSWORD = "password"
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:{DB_PASSWORD}@localhost:3306/{DB_NAME}"
SQLALCHEMY_ECHO = 0
# Jinja configurations
TEMPLATES_AUTO_RELOAD = 1
J2_LINE_STATEMENT_PREFIX = '#'

