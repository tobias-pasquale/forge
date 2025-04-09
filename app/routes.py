from flask import Blueprint, render_template, redirect, url_for
from app import db
from app.models import Session
from app.forms import SessionForm

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
    return render_template('index.html', form=form, sessions=sessions)
