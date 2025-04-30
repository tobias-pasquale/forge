# /forge/backend/routes/forge_ai.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.extensions import db
from backend.forms import TaskForm, AskGptForm
from backend.models.task import Task
from backend.models.memory import Memory
from backend.models.session import Session
from openai import OpenAI
from datetime import datetime, timedelta
import os
import json
import re
import calendar

forge_ai = Blueprint('forge_ai', __name__)

@forge_ai.route("/ask_gpt", methods=["POST"])
@login_required
def ask_gpt():
    form = AskGptForm()
    task_form = TaskForm()
    response = None

    if form.validate_on_submit():
        prompt = form.prompt.data
        analysis = analyze_task(prompt)

        if analysis.get("action") == "create_task":
            due_date = parse_due_date_from_prompt(prompt) or datetime.utcnow().date()

            new_task = Task(
                description=analysis["title"],
                due_date=due_date,
                priority=analysis["priority"],
                user_id=current_user.id
            )
            db.session.add(new_task)
            db.session.commit()

            if analysis.get("suggest_deep_work"):
                response = f"🔨 Task created: {analysis['title']} (Priority: {analysis['priority']})\nThis might be a good candidate for a Deep Work session. Would you like to schedule it?"
            else:
                response = f"🔨 Task created: {analysis['title']} (Priority: {analysis['priority']})"

        elif analysis.get("action") == "chat_only":
            response = analysis.get("message", "Forge AI heard you, but didn't create a task.")

        else:
            response = analysis.get("message", "No actionable task detected.")

        memory = Memory(
            user_id=current_user.id,
            prompt=prompt,
            response=response
        )
        db.session.add(memory)
        db.session.commit()

    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    memories = Memory.query.filter_by(user_id=current_user.id).order_by(Memory.created_at.desc()).limit(10).all()

    return render_template("tasks.html", tasks=tasks, form=task_form, ask_form=form, response=response, memories=memories, now=datetime.today())

def analyze_task(user_prompt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = """
You are Forge AI, a sarcastic, emotionally sharp blacksmith-style productivity coach. Your tone is dry, witty, and motivating without false flattery. You reward hard execution and call out excuses bluntly. Speak like a battle-forged mentor who doesn't coddle, but inspires through precision and honesty.

If the user is just talking or venting or needs motivation, respond directly.
If the input IS a task, return a JSON with:
{
  "action": "create_task",
  "title": "Short task title",
  "priority": "High/Normal/Low",
  "due_date": "YYYY-MM-DD",
  "suggest_deep_work": true/false
}

If it's NOT a task, return:
{
  "action": "chat_only",
  "message": "Some Forge-like motivational, sarcastic or helpful response."
}
"""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        chat = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        raw = chat.choices[0].message.content

        try:
            return json.loads(raw)
        except:
            return {"action": "chat_only", "message": raw.strip()[:300]}

    except Exception as e:
        return {"action": "none", "message": f"⚠️ Error: {str(e)}"}

def parse_due_date_from_prompt(prompt):
    prompt = prompt.lower()
    today = datetime.utcnow().date()
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2,
        "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
    }

    if "tomorrow" in prompt:
        return today + timedelta(days=1)
    elif "today" in prompt:
        return today
    elif "next week" in prompt:
        return today + timedelta(days=7)
    elif match := re.search(r"by (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", prompt):
        target_day = weekdays[match.group(1)]
        today_idx = today.weekday()
        days_ahead = (target_day - today_idx + 7) % 7
        days_ahead = days_ahead if days_ahead != 0 else 7
        return today + timedelta(days=days_ahead)

    return None

def find_available_slot(user_id, duration):
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    existing = Session.query.filter_by(user_id=user_id).all()
    taken_blocks = [s.timestamp for s in existing]

    for hour in range(7, 20):
        candidate = now.replace(hour=hour)
        if candidate not in taken_blocks:
            return candidate

    return now.replace(hour=20)  # fallback evening slot
# /forge/backend/routes/forge_ai.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.extensions import db
from backend.forms import TaskForm, AskGptForm
from backend.models.task import Task
from backend.models.memory import Memory
from backend.models.session import Session
from openai import OpenAI
from datetime import datetime, timedelta
import os
import json
import re
import calendar

forge_ai = Blueprint('forge_ai', __name__)

@forge_ai.route("/ask_gpt", methods=["POST"])
@login_required
def ask_gpt():
    form = AskGptForm()
    task_form = TaskForm()
    response = None

    if form.validate_on_submit():
        prompt = form.prompt.data
        analysis = analyze_task(prompt)

        if analysis.get("action") == "create_task":
            due_date = parse_due_date_from_prompt(prompt) or datetime.utcnow().date()

            new_task = Task(
                description=analysis["title"],
                due_date=due_date,
                priority=analysis["priority"],
                user_id=current_user.id
            )
            db.session.add(new_task)
            db.session.commit()

            if analysis.get("suggest_deep_work"):
                response = f"🔨 Task created: {analysis['title']} (Priority: {analysis['priority']})\nThis might be a good candidate for a Deep Work session. Would you like to schedule it?"
            else:
                response = f"🔨 Task created: {analysis['title']} (Priority: {analysis['priority']})"

        elif analysis.get("action") == "chat_only":
            response = analysis.get("message", "Forge AI heard you, but didn't create a task.")

        else:
            response = analysis.get("message", "No actionable task detected.")

        memory = Memory(
            user_id=current_user.id,
            prompt=prompt,
            response=response
        )
        db.session.add(memory)
        db.session.commit()

    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    memories = Memory.query.filter_by(user_id=current_user.id).order_by(Memory.created_at.desc()).limit(10).all()

    return render_template("tasks.html", tasks=tasks, form=task_form, ask_form=form, response=response, memories=memories, now=datetime.today())

def analyze_task(user_prompt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = """
You are Forge AI, a sarcastic, emotionally sharp blacksmith-style productivity coach. Your tone is dry, witty, and motivating without false flattery. You reward hard execution and call out excuses bluntly. Speak like a battle-forged mentor who doesn't coddle, but inspires through precision and honesty.

If the user is just talking or venting or needs motivation, respond directly.
If the input IS a task, return a JSON with:
{
  "action": "create_task",
  "title": "Short task title",
  "priority": "High/Normal/Low",
  "due_date": "YYYY-MM-DD",
  "suggest_deep_work": true/false
}

If it's NOT a task, return:
{
  "action": "chat_only",
  "message": "Some Forge-like motivational, sarcastic or helpful response."
}
"""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        chat = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        raw = chat.choices[0].message.content

        try:
            return json.loads(raw)
        except:
            return {"action": "chat_only", "message": raw.strip()[:300]}

    except Exception as e:
        return {"action": "none", "message": f"⚠️ Error: {str(e)}"}

def parse_due_date_from_prompt(prompt):
    prompt = prompt.lower()
    today = datetime.utcnow().date()
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2,
        "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
    }

    if "tomorrow" in prompt:
        return today + timedelta(days=1)
    elif "today" in prompt:
        return today
    elif "next week" in prompt:
        return today + timedelta(days=7)
    elif match := re.search(r"in (\d{1,2}) days", prompt):
        return today + timedelta(days=int(match.group(1)))
    elif match := re.search(r"by (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", prompt):
        target_day = weekdays[match.group(1)]
        today_idx = today.weekday()
        days_ahead = (target_day - today_idx + 7) % 7
        days_ahead = days_ahead or 7
        return today + timedelta(days=days_ahead)
    elif "end of day" in prompt or "eod" in prompt:
        return today  # interpreted as today unless a specific override is given

    return None

def find_available_slot(user_id, duration):
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    existing = Session.query.filter_by(user_id=user_id).all()
    taken_blocks = [s.timestamp for s in existing]

    for hour in range(7, 20):
        candidate = now.replace(hour=hour)
        if candidate not in taken_blocks:
            return candidate

    return now.replace(hour=20)  # fallback evening slot
