from backend import create_app
from backend.extensions import db
from sqlalchemy import text

from backend.models.user import User
from backend.models.task import Task
from backend.models.memory import Memory
from backend.models.session import Session

app = create_app()

with app.app_context():
    # First create all defined models
    db.create_all()
    db.session.commit()  # 👈 forces actual schema creation before raw SQL

    print("✅ Schema check complete.")
