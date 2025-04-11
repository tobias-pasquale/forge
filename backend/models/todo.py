from datetime import datetime
from backend.extensions import db

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    # completed_at = db.Column(db.DateTime, nullable=True)  # ✅ This line is new

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='Normal')  # Optional

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Optional: backref lets you say user.todos
    user = db.relationship("User", backref="todos")
