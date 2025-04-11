from dotenv import load_dotenv

load_dotenv()
import os
from flask import Flask
from backend.extensions import db, csrf, login_manager
from backend.routes import main


def create_app():
    # ✅ Tell Flask where to find templates
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, '..', 'frontend', 'templates')

    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object('config.Config')

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    app.login_manager = login_manager  # ✅ Add this line
    login_manager.login_view = 'main.login'  # 👈 redirects to login page

    app.register_blueprint(main)

    from backend.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
