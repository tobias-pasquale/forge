from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SubmitField, PasswordField, SelectField, DateField
from wtforms.validators import DataRequired, NumberRange, Email, EqualTo

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

class ToDoForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    due_date = DateField("Due Date", format='%Y-%m-%d', validators=[], render_kw={"placeholder": "YYYY-MM-DD"})
    priority = SelectField("Priority", choices=[("Low", "Low"), ("Normal", "Normal"), ("High", "High")])
    submit = SubmitField("Add Task")

class AskGptForm(FlaskForm):
    prompt = TextAreaField("Ask Forge AI", validators=[DataRequired()])
    submit = SubmitField("Submit")