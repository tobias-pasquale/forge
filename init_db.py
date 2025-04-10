from backend import create_app
from backend.extensions import db

app = create_app()
with app.app_context():
    # db.drop_all()
    db.create_all()
    print("✅ PostgreSQL schema recreated with latest models.")
