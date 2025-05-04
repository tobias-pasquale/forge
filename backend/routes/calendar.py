# /forge/backend/routes/calendar.py

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from backend.models.task import Task
from backend.models.session import Session
from backend.extensions import db
from datetime import datetime, timedelta

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

@calendar_bp.route('/calendar/events', methods=['GET', 'POST'])
@login_required
def calendar_events():
    if request.method == 'GET':
        sessions = Session.query.filter_by(user_id=current_user.id).all()
        tasks = Task.query.filter_by(user_id=current_user.id, completed=False).all()

        events = []

        for s in sessions:
            events.append({
                "id": f"session-{s.id}",
                "title": f"Deep Work: {s.category or 'Focus'}",
                "start": s.timestamp.isoformat(),
                "end": (s.timestamp + timedelta(minutes=s.duration)).isoformat(),
                "description": s.notes or '',
                "color": "#0d6efd",
                "allDay": False
            })

        for t in tasks:
            # Try to anchor off start_datetime first
            if t.start_datetime:
                start_dt = t.start_datetime
                end_dt = t.end_datetime or (start_dt + timedelta(minutes=t.estimated_minutes or 30))
            elif t.due_date:
                start_dt = datetime.combine(t.due_date, datetime.min.time()) + timedelta(hours=8)
                end_dt = start_dt + timedelta(minutes=t.estimated_minutes or 30)
            else:
                continue  # Skip if no reasonable date

            color = (
                "rgba(176, 42, 55, 0.5)" if t.priority == "High" else
                "rgba(217, 164, 6, 0.5)" if t.priority == "Normal" else
                "rgba(90, 98, 104, 0.5)"
            )

            events.append({
                "id": f"task-{t.id}",
                "title": f"Task: {t.description}",
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "description": t.description,
                "priority": t.priority,
                "color": color,
                "allDay": False
            })

        return jsonify(events)

    elif request.method == 'POST':
        data = request.get_json()
        start = datetime.fromisoformat(data.get('start')).replace(tzinfo=None)
        end = datetime.fromisoformat(data.get('end')).replace(tzinfo=None) if data.get('end') else start + timedelta(minutes=30)

        task = Task(
            description=data.get('title'),
            start_datetime=start,
            end_datetime=end,
            estimated_minutes=int((end - start).total_seconds() // 60),
            priority='Normal',
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({"status": "success", "id": task.id})

@calendar_bp.route('/calendar/events/<id>', methods=['PUT', 'DELETE'])
@login_required
def update_or_delete_event(id):
    is_task = id.startswith("task-")
    pure_id = int(id.split('-')[-1])

    if request.method == 'PUT':
        data = request.get_json()
        start = datetime.fromisoformat(data.get('start')).replace(tzinfo=None)
        end = datetime.fromisoformat(data.get('end')).replace(tzinfo=None) if data.get('end') else start + timedelta(minutes=30)

        if is_task:
            task = Task.query.get_or_404(pure_id)
            if task.user_id != current_user.id:
                return jsonify({"error": "Unauthorized"}), 403

            task.start_datetime = start
            task.end_datetime = end
            task.estimated_minutes = int((end - start).total_seconds() // 60)
            task.description = data.get('title', task.description)
            db.session.commit()
            return jsonify({"status": "updated"})

        else:
            session = Session.query.get_or_404(pure_id)
            if session.user_id != current_user.id:
                return jsonify({"error": "Unauthorized"}), 403

            session.timestamp = start
            session.duration = int((end - start).total_seconds() // 60)
            db.session.commit()
            return jsonify({"status": "updated"})

    elif request.method == 'DELETE':
        if is_task:
            task = Task.query.get_or_404(pure_id)
            if task.user_id != current_user.id:
                return jsonify({"error": "Unauthorized"}), 403
            db.session.delete(task)
            db.session.commit()
            return jsonify({"status": "deleted"})

        else:
            session = Session.query.get_or_404(pure_id)
            if session.user_id != current_user.id:
                return jsonify({"error": "Unauthorized"}), 403
            db.session.delete(session)
            db.session.commit()
            return jsonify({"status": "deleted"})
