# /forge/backend/routes/tasks.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.task import Task
from backend.models.calendar_event import CalendarEvent
from datetime import datetime, timedelta, date
from backend.forms import TaskForm
import pytz

tasks = Blueprint('tasks', __name__)

@tasks.route('/tasks', methods=['GET', 'POST'])
@login_required
def view_tasks():
    form = TaskForm()
    local_now = datetime.now()
    today = local_now.date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    all_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    completed = [t for t in all_tasks if t.completed]
    streak = len([t for t in completed if t.completed_at and t.completed_at.date() == today])

    events = CalendarEvent.query.filter_by(user_id=current_user.id).filter(
        CalendarEvent.start_time >= start_of_day,
        CalendarEvent.start_time <= end_of_day
    ).order_by(CalendarEvent.start_time.asc()).all()

    todays_tasks = Task.query.filter_by(user_id=current_user.id, completed=False).filter(
        Task.start_datetime >= start_of_day,
        Task.start_datetime <= end_of_day
    ).order_by(Task.start_datetime.asc()).all()

    if form.validate_on_submit():
        # Create new task based on simple form
        new_task = Task(
            user_id=current_user.id,
            description=form.task.data,
            priority=form.priority.data,
            recurring=form.recurring.data,
            completed=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        from backend.routes.forge_ai import estimate_task_time
        estimated_minutes = estimate_task_time(new_task.description)
        new_task.estimated_minutes = estimated_minutes or 30

        if form.end_datetime.data:
            due_date = form.end_datetime.data
            start_time_default = datetime.combine(due_date, datetime.min.time()) + timedelta(hours=8)
            new_task.start_datetime = start_time_default
            new_task.end_datetime = start_time_default + timedelta(minutes=new_task.estimated_minutes)

        db.session.add(new_task)
        db.session.commit()

        if new_task.start_datetime:
            event = CalendarEvent(
                user_id=current_user.id,
                title=new_task.description,
                start_time=new_task.start_datetime,
                end_time=new_task.end_datetime,
                event_type='Task'
            )
            db.session.add(event)
            db.session.commit()

        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks.view_tasks'))

    tomorrow = today + timedelta(days=1)
    return render_template(
        'tasks.html',
        tasks=all_tasks,
        form=form,
        completed_tasks=completed,
        streak=streak,
        calendar_events=events,
        now=local_now,
        tomorrow=tomorrow
    )

@tasks.route('/add', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('task')
    if title:
        new_task = Task(title=title, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added.')
    return redirect(url_for('tasks.view_tasks'))

@tasks.route('/update/<int:task_id>')
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    local_now = datetime.now()
    if task.user_id == current_user.id:
        task.completed = not task.completed
        task.completed_at = local_now if task.completed else None
        db.session.commit()
        flash('Task status updated.')
    return redirect(url_for('tasks.view_tasks'))

@tasks.route('/edit_task/<int:task_id>', methods=['POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('tasks.view_tasks'))

    task_desc = request.form.get("edited_task")
    start_datetime = request.form.get("edited_start_datetime")
    end_datetime = request.form.get("edited_end_datetime")
    priority = request.form.get("edited_priority")
    recurring = request.form.get("edited_recurring")

    if task_desc:
        task.description = task_desc
    if start_datetime:
        task.start_datetime = datetime.fromisoformat(start_datetime)
    if end_datetime:
        task.end_datetime = datetime.fromisoformat(end_datetime)
    if priority:
        task.priority = priority
    if recurring:
        task.recurring = recurring

    db.session.commit()
    flash("Task updated.", "success")
    return redirect(url_for('tasks.view_tasks'))

@tasks.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('tasks.view_tasks'))

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "info")
    return redirect(url_for('tasks.view_tasks'))

@tasks.route('/toggle_task/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    task.completed = data.get('completed', False)
    task.completed_at = datetime.utcnow() if task.completed else None

    new_task = None
    if task.completed and task.recurring and task.recurring != 'None':
        new_start = (task.start_datetime or datetime.utcnow()) + timedelta(days=1)
        new_end = (task.end_datetime or (task.start_datetime + timedelta(minutes=task.estimated_minutes or 30))) + timedelta(days=1)

        new_task = Task(
            description=task.description,
            start_datetime=new_start,
            end_datetime=new_end,
            priority=task.priority,
            recurring=task.recurring,
            user_id=task.user_id,
            completed=False
        )
        db.session.add(new_task)

    db.session.commit()

    response = {
        'status': 'success',
        'completed': task.completed
    }

    if new_task:
        response.update({
            'new_task_id': new_task.id,
            'description': new_task.description,
            'recurring': new_task.recurring
        })

    return jsonify(response)

@tasks.route('/tasks/todays_calendar_events')
@login_required
def todays_calendar_events():
    local_now = datetime.now()
    today = local_now.date()

    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    # Fetch today's tasks
    tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.start_datetime >= start_of_day,
        Task.start_datetime <= end_of_day,
        Task.completed == False  # Only active tasks
    ).all()

    # Format them for FullCalendar
    events = []
    for t in tasks:
        events.append({
            "id": f"task-{t.id}",
            "title": t.description,
            "start": t.start_datetime.isoformat(),
            "end": (t.end_datetime.isoformat() if t.end_datetime else None),
            "color": "#ffc107",  # yellowish
        })

    return jsonify(events)

@tasks.route('/tasks/partial_task_list')
@login_required
def task_list_partial():
    # Re-query all tasks and render just the partial
    all_tasks = Task.query \
        .filter_by(user_id=current_user.id) \
        .order_by(Task.created_at.desc()) \
        .all()

    now = datetime.now()
    tomorrow = now.date() + timedelta(days=1)

    return render_template(
        'partials/task_list.html',
        tasks=all_tasks,
        now=now,
        tomorrow=tomorrow
    )