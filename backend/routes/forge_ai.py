# /forge/backend/routes/forge_ai.py

import os
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from backend.models.task import Task
from backend.models.session import Session
from backend.models.memory import Memory
from backend.forms import AskGptForm, TaskForm
from backend.extensions import db
from openai import OpenAI
from datetime import datetime, timedelta
from dateutil import parser as date_parser

forge_ai = Blueprint('forge_ai', __name__)

@forge_ai.route("/ask_gpt", methods=["POST"])
@login_required
def ask_gpt():
    ask_form = AskGptForm()
    task_form = TaskForm()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = ask_form.prompt.data if ask_form.validate_on_submit() else None
    response = None

    user_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    user_sessions = Session.query.filter_by(user_id=current_user.id).order_by(Session.timestamp.desc()).limit(10).all()
    user_memory = Memory.query.filter_by(user_id=current_user.id).order_by(Memory.created_at.desc()).limit(7).all()

    task_summary = "\n".join([
        f"- {'[✔]' if t.completed else '[ ]'} {t.description} | Due: {t.due_date.strftime('%Y-%m-%d') if t.due_date else 'None'} | Priority: {t.priority or 'Normal'} | Recurring: {t.recurring or 'None'}"
        for t in user_tasks
    ])
    session_summary = "\n".join([
        f"- {s.timestamp.strftime('%Y-%m-%d')} | {s.duration} mins | Depth: {s.depth} | Impact: {s.impact} | Cat: {s.category or 'None'}"
        for s in user_sessions
    ])
    memory_snippets = "\n".join([
        f"User: {m.prompt}\nForge AI: {m.response}" for m in reversed(user_memory)
    ])

    instruction = f"""
    You are Forge AI — the sarcastic but intelligent blacksmith assistant inside the WarriorsForge system.
    Your job is to:
    - Analyze the user's input.
    - Detect if it is a task, vague idea, motivational request, or strategic planning input.
    - DO NOT create a task unless the user clearly intends to convert something into a task or action item.
    - Provide dry, motivational commentary on their progress.
    - Suggest improvements to their inputs if vague.
    - If you identify poor phrasing, offer cleaned-up versions, and ask if they want to convert it.

    Maintain tone: blunt, dry, direct, tactical. Your responses must be short, impactful, and not overly verbose.

    ---
    USER INPUT: "{prompt}"

    TASKS:
    {task_summary}

    DEEP WORK:
    {session_summary}

    MEMORY:
    {memory_snippets}

    Respond in the following format:

    1. **Assessment** — What the user seems to be doing (Planning, Reflecting, Avoiding, Asking for Help).
    2. **Feedback** — If vague, suggest improvements. Be direct.
    3. **Options** — Ask if the user wants you to turn cleaned input into tasks or add calendar blocks (only if relevant).
    4. **Tone** — Always conclude with one sentence of blacksmith sarcasm or praise (if earned).
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Forge AI, the battle-hardened assistant in the WarriorsForge app."},
                {"role": "user", "content": instruction}
            ]
        )
        response = completion.choices[0].message.content
    except Exception as e:
        response = f"⚠️ Error: {str(e)}"

    db.session.add(Memory(user_id=current_user.id, prompt=prompt, response=response))
    db.session.commit()

    return render_template(
        "ai_chat.html",
        tasks=user_tasks,
        sessions=user_sessions,
        form=task_form,
        ask_form=ask_form,
        response=response,
        streak=calculate_streak(user_tasks),
        now=datetime.utcnow().date()
    )


@forge_ai.route("/ai", methods=["GET"], endpoint="ai_chat")
@login_required
def blacksmith_page():
    task_form = TaskForm()
    ask_form = AskGptForm()
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).limit(5).all()
    sessions = Session.query.filter_by(user_id=current_user.id).order_by(Session.timestamp.desc()).limit(5).all()

    return render_template(
        "ai_chat.html",
        tasks=tasks,
        sessions=sessions,
        form=task_form,
        ask_form=ask_form,
        response=None,
        streak=calculate_streak(tasks),
        now=datetime.utcnow().date()
    )

def calculate_streak(tasks):
    days = {t.created_at.date() for t in tasks if t.completed}
    today = datetime.utcnow().date()
    streak = 0
    while today in days:
        streak += 1
        today -= timedelta(days=1)
    return streak
