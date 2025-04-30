# /forge/backend/routes/tasks.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.task import Task
from datetime import datetime
from backend.forms import TaskForm

tasks = Blueprint('tasks', __name__)

@tasks.route('/tasks', methods=['GET', 'POST'])
@login_required
def view_tasks():
    form = TaskForm()

    if form.validate_on_submit():
        new_task = Task(
            description=form.task.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            recurring=form.recurring.data,
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task added.', 'success')
        return redirect(url_for('tasks.view_tasks'))

    all_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('tasks.html', tasks=all_tasks, form=form)

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
    due_date = request.form.get("edited_due_date")
    priority = request.form.get("edited_priority")
    recurring = request.form.get("edited_recurring")

    if task_desc:
        task.description = task_desc

    if due_date:
        task.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()

    task.priority = priority
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
    db.session.commit()
    return jsonify({'status': 'success', 'completed': task.completed})
