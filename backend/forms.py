from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SubmitField, PasswordField, SelectField, DateField, DateTimeField
from wtforms.validators import DataRequired, NumberRange, Email, EqualTo
from datetime import date, datetime

class SessionForm(FlaskForm):
    duration = FloatField('Duration (hrs)', validators=[DataRequired()])
    depth = IntegerField('Depth (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    impact = IntegerField('Impact (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    category = StringField('Category')
    notes = TextAreaField('Notes')
    submit = SubmitField('Log Session')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

class TaskForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    description = TextAreaField("Description")
    end_datetime = DateTimeField("Due Date/Time", default=datetime.utcnow)  # Notice: DateTimeField
    priority = SelectField("Priority", choices=[("None", "None"), ("Normal", "Normal"), ("High", "High")], default="Normal")
    recurring = SelectField('Recurring', choices=[
        ('None', 'None'),
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly')
    ], default='None')
    submit = SubmitField("Add Task")

class AskGptForm(FlaskForm):
    prompt = TextAreaField("Ask Forge AI", validators=[DataRequired()])
    submit = SubmitField("Submit")