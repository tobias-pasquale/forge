# /forge/backend/models/task.py

from datetime import datetime
from backend.extensions import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), default='Normal')
    recurring = db.Column(db.String(20), default='None')
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    estimated_minutes = db.Column(db.Integer, nullable=True)  # minutes

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref="tasks")
