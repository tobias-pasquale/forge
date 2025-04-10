from flask import Blueprint, render_template, redirect, url_for, flash, request
from collections import Counter

from backend.forms import SessionForm, RegisterForm
from backend.models.session import Session
from backend.models.user import User

main = Blueprint('main', __name__)

print("✔️ ROUTES LOADED")

@main.route('/', methods=['GET', 'POST'])
def index():
    from backend import db  # 👈 lazy import to avoid circular import

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
    avg_impact = round(sum(s.impact for s in sessions) / len(sessions) , 2) if sessions else 0

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

@main.route('/register', methods=['GET', 'POST'])
def register():
    from backend import db  # 👈 same here

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('main.index'))
    return render_template('register.html', form=form)
