from backend import create_app
from backend.extensions import db

from backend.models.user import User
from backend.models.todo import ToDo
from backend.models.memory import Memory

app = create_app()
with app.app_context():
    # db.drop_all()
    db.create_all()
    print("✅ PostgreSQL schema recreated with latest models.")
