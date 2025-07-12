from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SkillForm(FlaskForm):
    name = StringField('Skill Name', validators=[DataRequired(), Length(max=100)])
    skill_type = SelectField('Type', choices=[('offered', 'Offering'), ('wanted', 'Seeking')], validators=[DataRequired()])
    availability = StringField('Availability (e.g., Weekends, Evenings)', validators=[Length(max=100)])
    submit = SubmitField('Add Skill')

class SwapRequestForm(FlaskForm):
    message = TextAreaField('Message (Optional)', validators=[Length(max=500)])
    submit = SubmitField('Send Request')

class ProfileSettingsForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=4, max=64)])
    location = StringField('Location', validators=[Length(max=100)])
    is_public = BooleanField('Make Profile Public')
    submit = SubmitField('Update Settings')
