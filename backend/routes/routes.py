from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from collections import Counter
from backend import db
from backend.forms import SessionForm, RegisterForm, LoginForm, ToDoForm
from backend.models.session import Session
from backend.models.user import User
from backend.models.todo import ToDo
from openai import OpenAI
import os

main = Blueprint('main', __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("✔️ ROUTES LOADED")

@main.route("/", methods=["GET", "POST"])
@login_required
def index():

    from backend import db  # 👈 lazy import to avoid circular import
    form = SessionForm()
    if form.validate_on_submit():
        session = Session(
            duration=form.duration.data,
            depth=form.depth.data,
            impact=form.impact.data,
            category=form.category.data,
            notes=form.notes.data,
            user_id=current_user.id
        )
        db.session.add(session)
        db.session.commit()
        return redirect(url_for("main.index"))

    sessions = Session.query.filter_by(user_id=current_user.id).order_by(Session.timestamp.desc()).all()
    total_hours = sum(s.duration for s in sessions)
    avg_depth = round(sum(s.depth for s in sessions) / len(sessions), 2) if sessions else 0
    avg_impact = round(sum(s.impact for s in sessions) / len(sessions), 2) if sessions else 0
    categories = [s.category for s in sessions if s.category]
    top_category = Counter(categories).most_common(1)[0][0] if categories else "None"

    return render_template("index.html", form=form, sessions=sessions, total_hours=total_hours,
                           avg_depth=avg_depth, avg_impact=avg_impact, top_category=top_category)

@main.route("/register", methods=["GET", "POST"])
def register():
    from backend import db  # 👈 same here
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)

@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("main.login"))

@main.route("/todo", methods=["GET", "POST"])
@login_required
def todo():
    form = ToDoForm()
    if form.validate_on_submit():
        new_task = ToDo(task=form.task.data, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash("Task added!", "success")
        return redirect(url_for("main.todo"))

    tasks = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.created_at.desc()).all()
    streak = calculate_streak(tasks)
    message = None
    if streak >= 3:
        message = f"🔥 You're on a {streak}-day streak! Keep it up!"
    elif streak == 1:
        message = "✅ You knocked out a task today—don’t break the chain!"

    return render_template("todo.html", tasks=tasks, form=form, streak=streak, message=message)

@main.route("/todo/complete/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    task = ToDo.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("main.todo"))
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for("main.todo"))

@main.route("/todo/ask", methods=["POST"])
@login_required
def ask_gpt():
    prompt = request.form.get("prompt")
    response = None

    if prompt:
        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Replace with "gpt-4" if you have access
                messages=[
                    {"role": "system", "content": "You are Forge AI, a motivational productivity coach."},
                    {"role": "user", "content": prompt}
                ]
            )
            response = completion.choices[0].message.content
        except Exception as e:
            response = f"⚠️ Error: {str(e)}"

    tasks = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.created_at.desc()).all()
    form = ToDoForm()
    streak = calculate_streak(tasks)
    return render_template("todo.html", tasks=tasks, form=form, response=response, streak=streak)

def calculate_streak(tasks):
    days = {t.created_at.date() for t in tasks if t.completed}
    today = datetime.utcnow().date()
    streak = 0
    while today in days:
        streak += 1
        today -= timedelta(days=1)
    return streak

