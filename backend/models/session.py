from backend.extensions import db
from datetime import datetime

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Float, nullable=False)
    depth = db.Column(db.Integer, nullable=False)
    impact = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(64))
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)