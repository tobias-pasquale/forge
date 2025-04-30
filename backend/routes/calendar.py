# /forge/backend/routes/calendar.py

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from backend.models.task import Task
from backend.models.session import Session
from datetime import timedelta

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

@calendar_bp.route('/calendar/events')
@login_required
def calendar_events():
    sessions = Session.query.filter_by(user_id=current_user.id).all()
    tasks = Task.query.filter_by(user_id=current_user.id).all()

    events = []

    # Deep Work Sessions
    for s in sessions:
        events.append({
            "title": f"Deep Work – {s.category or 'Focus'}",
            "start": s.timestamp.isoformat(),
            "end": (s.timestamp + timedelta(minutes=s.duration)).isoformat(),
            "color": "#0d6efd"  # Bootstrap blue
        })

    # Tasks with due dates
    for t in tasks:
        if t.due_date and not t.completed:
            events.append({
                "title": f"Task – {t.description[:30]}",
                "start": t.due_date.isoformat(),
                "allDay": True,
                "color": "#fd7e14"  # Bootstrap orange
            })

    return jsonify(events)


# 🔧 To activate:
# - Register `calendar_bp` in backend/__init__.py
# - Create calendar.html
# - Mount FullCalendar in that template
# - Add a link to the calendar in base.html

# Optional route to serve static or dynamic views of past/future performance.
