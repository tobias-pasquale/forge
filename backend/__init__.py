import os
from flask import Flask
from backend.extensions import db, csrf
from backend.routes import main
from dotenv import load_dotenv

load_dotenv()

def create_app():
    # ✅ Tell Flask where to find templates
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, '..', 'frontend', 'templates')

    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object('config.Config')

    db.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(main)

    return app
