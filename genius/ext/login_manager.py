from flask_login import LoginManager
from genius.db.model import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()

