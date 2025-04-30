import os
from flask import Flask
from backend.extensions import db, csrf, login_manager
from backend.routes import core, auth, tasks, forge_ai, calendar_bp
from dotenv import load_dotenv

load_dotenv()

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, '..', 'backend', 'templates')

    app = Flask(__name__, static_folder="../frontend/static", template_folder=template_dir)
    app.config.from_object('config.Config')

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    app.login_manager = login_manager
    login_manager.login_view = 'auth.login'  # ✅ Fixed this line

    app.register_blueprint(core)
    app.register_blueprint(auth)
    app.register_blueprint(tasks)
    app.register_blueprint(forge_ai)
    app.register_blueprint(calendar_bp)

    from backend.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
