from backend.extensions import db
from datetime import datetime
from flask_login import UserMixin

class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<CalendarEvent {self.title} {self.start_time}>'
