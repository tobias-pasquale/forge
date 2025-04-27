from flask import Blueprint, render_template, redirect, url_for, flash, request
from dotenv import load_dotenv
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta, date
from collections import Counter
from backend import db
from backend.forms import SessionForm, RegisterForm, LoginForm, ToDoForm, AskGptForm
from backend.models.session import Session
from backend.models.user import User
from backend.models.todo import ToDo


import os

main = Blueprint('main', __name__)


print("✔️ ROUTES LOADED")

@main.route("/")
def home():
    return render_template("home.html")

@main.route("/focus", methods=["GET", "POST"])
@login_required
def index():
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
    ask_form = AskGptForm()
    if form.validate_on_submit():
        task_text = form.task.data
        due_date = form.due_date.data
        priority = form.priority.data

        new_task = ToDo(
            task=task_text,
            due_date=due_date,
            priority=priority,
            recurring=form.recurring.data,
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        flash("Task added.", "success")
        return redirect(url_for("main.todo"))

    tasks = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.created_at.desc()).all()
    streak = calculate_streak(tasks)
    message = None
    if streak >= 3:
        message = f"🔥 You're on a {streak}-day streak! Keep it up!"
    elif streak == 1:
        message = "✅ You knocked out a task today—don’t break the chain!"
    
    
    return render_template(
        "todo.html",
        tasks=tasks,
        form=form,
        ask_form=ask_form,
        streak=streak,
        message=message,
        current_date=date.today().isoformat(),
        now=date.today()
    )

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
    from openai import OpenAI
    from backend.models.memory import Memory
    from backend import db

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    ask_form = AskGptForm()
    todo_form = ToDoForm()
    response = None

    if ask_form.validate_on_submit():
        prompt = ask_form.prompt.data

        # 🧠 Fetch user's To-Do list to provide memory/context
        user_tasks = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.created_at.desc()).all()
        task_list_summary = "\n".join([
            f"- {'[✔]' if t.completed else '[ ]'} {t.task} | Due: {t.due_date.strftime('%b %d') if t.due_date else 'N/A'} | Priority: {t.priority or 'Normal'} | Recurring: {t.recurring or 'None'}"
            for t in user_tasks
        ])
        sessions = Session.query.filter_by(user_id=current_user.id).order_by(Session.timestamp.desc()).limit(10).all()
        deep_summary = "\n".join([
            f"- {s.timestamp.strftime('%b %d')} | {s.duration} mins | Depth: {s.depth} | Impact: {s.impact} | Cat: {s.category or 'N/A'}"
            for s in sessions
        ])

        # 🧠 Inject context into prompt
        contextual_prompt = f"""
        You are Forge AI, a motivational productivity assistant designed to push users toward intentional, disciplined focus and execution.

        Here is the current To-Do list for the user:

        {task_list_summary}

        Here is the current Deep Work Logs for the user:
        
        {deep_summary}

        The user just asked: "{prompt}"

        Respond in a stoic tone. You may suggest priorities, note patterns, or offer encouragement based on their tasks.
        """

        try:
            # 🧠 Grab last 7 interactions for context
            past = Memory.query.filter_by(user_id=current_user.id)\
                .order_by(Memory.created_at.desc())\
                .limit(7).all()

            memory_snippets = "\n".join([
                f"User: {m.prompt}\nForge AI: {m.response}" for m in reversed(past)
            ])

            contextual_prompt_with_memory = f"""
            You are Forge AI, a motivating productivity assistant. You remember what the user has asked you recently and use that context to provide helpful, insightful responses.

            Recent memory:
            {memory_snippets}

            Current To-Do List:
            {task_list_summary}

            The user just asked: "{prompt}"
            """

            # 🧠 Call OpenAI with full context
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Forge AI, a productivity coach that adapts based on memory and user task data."},
                    {"role": "user", "content": contextual_prompt_with_memory}
                ]
            )

            response = completion.choices[0].message.content

        except Exception as e:
            response = f"⚠️ Error: {str(e)}"

        # 🧠 Log the prompt/response to memory regardless of success or fail
        new_memory = Memory(
            user_id=current_user.id,
            prompt=prompt,
            response=response
        )

        db.session.add(new_memory)
        db.session.commit()

    # 🧠 Rebuild template context
    tasks = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.created_at.desc()).all()
    streak = calculate_streak(tasks)
    memories = Memory.query.filter_by(user_id=current_user.id)\
        .order_by(Memory.created_at.desc())\
        .limit(20).all()
    
    import traceback
    print(traceback.format_exc())


    return render_template(
        "todo.html",
        tasks=tasks,
        form=todo_form,
        ask_form=ask_form,
        response=response,
        streak=streak,
        memories=memories,
        now=date.today()
    )


def calculate_streak(tasks):
    days = {t.created_at.date() for t in tasks if t.completed}
    today = datetime.utcnow().date()
    streak = 0
    while today in days:
        streak += 1
        today -= timedelta(days=1)
    return streak


@main.route('/edit_task/<int:task_id>', methods=['POST'])
@login_required
def edit_task(task_id):
    from backend import db
    task = ToDo.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.todo'))

    task_desc = request.form.get("edited_task")
    due_date = request.form.get("edited_due_date")
    priority = request.form.get("edited_priority")
    recurring = request.form.get("edited_recurring")

    if task_desc:
        task.task = task_desc

    if due_date:
        from datetime import datetime
        task.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()

    task.priority = priority
    task.recurring = recurring

    db.session.commit()
    flash("Task updated.", "success")
    return redirect(url_for('main.todo'))

@main.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    from backend import db
    task = ToDo.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.todo'))

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "info")
    return redirect(url_for('main.todo'))

@main.route("/creed")
@login_required
def creed():
    return render_template("creed.html")

@main.route('/toggle_task/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    from backend import db
    task = ToDo.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        return {'error': 'Unauthorized'}, 403

    data = request.get_json()
    task.completed = data.get('completed', False)
    db.session.commit()
    return {'status': 'success', 'completed': task.completed}
