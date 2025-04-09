from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class SessionForm(FlaskForm):
    duration = FloatField('Duration (hrs)', validators=[DataRequired()])
    depth = IntegerField('Depth (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    impact = IntegerField('Impact (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    category = StringField('Category')
    notes = TextAreaField('Notes')
    submit = SubmitField('Log Session')
