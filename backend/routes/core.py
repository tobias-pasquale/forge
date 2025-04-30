# /forge/backend/routes/core.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from collections import Counter

core = Blueprint('core', __name__)

@core.route('/')
@login_required
def home():
    return redirect(url_for('core.dashboard'))

@core.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@core.route('/start_deep_work', methods=['POST'])
@login_required
def start_deep_work():
    flash('Deep Work Session Started. Stay strong.')
    return redirect(url_for('core.dashboard'))

@core.route('/creed')
@login_required
def creed():
    return render_template('creed.html')

@core.route('/focus', methods=['GET', 'POST'])
@login_required
def focus():
    from backend.forms import SessionForm
    from backend.models.session import Session

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
        flash("Session logged.", "success")
        return redirect(url_for("core.focus"))

    sessions = Session.query.filter_by(user_id=current_user.id).order_by(Session.timestamp.desc()).all()
    total_hours = sum(s.duration for s in sessions)
    avg_depth = round(sum(s.depth for s in sessions) / len(sessions), 2) if sessions else 0
    avg_impact = round(sum(s.impact for s in sessions) / len(sessions), 2) if sessions else 0
    categories = [s.category for s in sessions if s.category]
    top_category = Counter(categories).most_common(1)[0][0] if categories else "None"

    return render_template("focus.html", form=form, sessions=sessions, total_hours=total_hours,
                           avg_depth=avg_depth, avg_impact=avg_impact, top_category=top_category)
