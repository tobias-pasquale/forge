from flask import Blueprint, render_template, redirect, url_for
from app import db
from app.models import Session
from app.forms import SessionForm
from collections import Counter

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = SessionForm()
    if form.validate_on_submit():
        session = Session(
            duration=form.duration.data,
            depth=form.depth.data,
            impact=form.impact.data,
            category=form.category.data,
            notes=form.notes.data
        )
        db.session.add(session)
        db.session.commit()
        return redirect(url_for('main.index'))

    sessions = Session.query.order_by(Session.timestamp.desc()).all()
    # Summary stats
    total_hours = sum(s.duration for s in sessions)
    avg_depth = round(sum(s.depth for s in sessions) / len(sessions), 2) if sessions else 0
    avg_impact = round(sum(s.impact for s in sessions) / len(sessions), 2) if sessions else 0

    # Most frequent category
    categories = [s.category for s in sessions if s.category]
    most_common = Counter(categories).most_common(1)
    top_category = most_common[0][0] if most_common else "None"
    return render_template(
    'index.html',
    form=form,
    sessions=sessions,
    total_hours=total_hours,
    avg_depth=avg_depth,
    avg_impact=avg_impact,
    top_category=top_category
)