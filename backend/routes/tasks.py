# /forge/backend/routes/tasks.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.task import Task
from backend.models.calendar_event import CalendarEvent
from datetime import datetime, timedelta
from backend.forms import TaskForm


tasks = Blueprint('tasks', __name__)

@tasks.route('/tasks', methods=['GET', 'POST'])
@login_required
def view_tasks():
    form = TaskForm()
    all_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    completed = [t for t in all_tasks if t.completed]
    streak = len([t for t in completed if t.completed_at and t.completed_at.date() == datetime.utcnow().date()])

    today = datetime.utcnow().date()
    events = CalendarEvent.query.filter_by(user_id=current_user.id).filter(
        CalendarEvent.start_time >= datetime.combine(today, datetime.min.time()),
        CalendarEvent.start_time <= datetime.combine(today, datetime.max.time())
    ).order_by(CalendarEvent.start_time.asc()).all()

    if form.validate_on_submit():
        new_task = Task(
            user_id=current_user.id,
            description=form.description.data,
            start_datetime=form.start_datetime.data,
            end_datetime=form.end_datetime.data,
            priority=form.priority.data,
            recurring=form.recurring.data,
            category=form.category.data,
            difficulty=form.difficulty.data,
            estimated_minutes=form.estimated_minutes.data,
        )

        from backend.routes.forge_ai import estimate_task_time
        estimated_minutes = estimate_task_time(new_task.description)
        new_task.estimated_minutes = estimated_minutes or 30

        db.session.add(new_task)
        db.session.commit()

        if new_task.start_datetime:
            event = CalendarEvent(
                user_id=current_user.id,
                title=new_task.description,
                start_time=new_task.start_datetime,
                end_time=new_task.end_datetime or (new_task.start_datetime + timedelta(minutes=new_task.estimated_minutes or 30)),
                event_type='Task'
            )
            db.session.add(event)
            db.session.commit()

        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks.view_tasks'))

    all_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    now = datetime.utcnow()
    tomorrow = now + timedelta(days=1)
    return render_template(
        'tasks.html',
        tasks=all_tasks,
        form=form,
        completed_tasks=completed,
        streak=streak,
        calendar_events=events,
        now=now,
        tomorrow=tomorrow
    )

@tasks.route('/add', methods=['POST'])
@login_required
def add_task():
    description = request.form.get('description')
    if description:
        new_task = Task(description=description, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added.')
    return redirect(url_for('tasks.view_tasks'))

@tasks.route('/update/<int:task_id>')
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        task.completed = not task.completed
        task.completed_at = datetime.utcnow() if task.completed else None
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
