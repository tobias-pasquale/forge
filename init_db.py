from backend import create_app
from backend.extensions import db
from sqlalchemy import text

from backend.models.user import User
from backend.models.todo import ToDo
from backend.models.memory import Memory

app = create_app()

with app.app_context():
    # First create all defined models
    db.create_all()
    db.session.commit()  # 👈 forces actual schema creation before raw SQL

    # THEN check for 'recurring' column
    result = db.session.execute(
        text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='to_do'
            AND column_name='recurring'
        """)
    )

    if not result.first():
        db.session.execute(
            text("ALTER TABLE to_do ADD COLUMN recurring VARCHAR(20) DEFAULT 'None'")
        )
        db.session.commit()
        print("🛠️ Added 'recurring' column to 'to_do' table.")

    print("✅ Schema check complete.")
