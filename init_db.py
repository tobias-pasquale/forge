from backend import create_app
from backend.extensions import db
from sqlalchemy import inspect, text

from backend.models.user import User
from backend.models.task import Task
from backend.models.memory import Memory
from backend.models.session import Session
from backend.models.calendar_event import CalendarEvent

from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)

    # Drop all tables manually with CASCADE
    existing_tables = inspector.get_table_names()
    if existing_tables:
        print("⚠️ Dropping existing tables with CASCADE:")
        for table in existing_tables:
            print(f"  - Dropping: {table}")
            db.session.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
        db.session.commit()
    else:
        print("✅ No existing tables to drop.")

    # Recreate fresh tables
    db.create_all()
    db.session.commit()

    print("\n✅ New tables created:")
    for table in inspect(db.engine).get_table_names():
        print(f"  - Created: {table}")

    # Create admin user
    admin = User(
        username="Tobias",
        email="tobiaspasquale@gmail.com",
        password_hash=generate_password_hash("forgeadmin"),
    )
    db.session.add(admin)
    db.session.commit()

    print("\n👤 Admin user created: Tobias (tobiaspasquale@gmail.com)")

    # Seed example tasks
    sample_tasks = [
        Task(user_id=admin.id, description="Finish WarriorsForge MVP Plan", due_date=datetime.utcnow() + timedelta(days=1), priority="High"),
        Task(user_id=admin.id, description="30 min Deep Work on Forge Calendar", due_date=datetime.utcnow(), priority="Normal", recurring="Daily"),
        Task(user_id=admin.id, description="Read 1 Chapter of 'Tax-Free Wealth'", due_date=datetime.utcnow() + timedelta(days=2), priority="Normal"),
        Task(user_id=admin.id, description="Summarize Daily Victory, Mistake, Adjustment", due_date=datetime.utcnow(), recurring="Daily"),
    ]
    db.session.add_all(sample_tasks)
    db.session.commit()

    print("\n🛠 Sample tasks created:")
    for task in sample_tasks:
        print(f"  - {task.description}")

    print("\n🚀 Forge DB bootstrap complete. Ready for deployment.")
