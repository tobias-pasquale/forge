from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from backend.models.user import User

login_manager = LoginManager()
def load_user(user_id):
    return User.query.get(int(user_id))

db = SQLAlchemy()
csrf = CSRFProtect()
