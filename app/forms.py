from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectMultipleField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Length, Optional
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
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    skill_offered = StringField('Skill Offered', validators=[DataRequired(), Length(max=100)])
    skill_wanted = StringField('Skill Wanted', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    availability = SelectField('Availability', 
                              choices=[('weekends', 'Weekends'), 
                                     ('evenings', 'Evenings'), 
                                     ('weekdays', 'Weekdays'),
                                     ('flexible', 'Flexible')],
                              validators=[DataRequired()])
    location = StringField('Location (Optional)', validators=[Length(max=100)])
    submit = SubmitField('Add Skill')
class SwapRequestForm(FlaskForm):
    message = TextAreaField('Message (Optional)', validators=[Length(max=500)])
    submit = SubmitField('Send Request')



class ProfileSettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    skills_offered = TextAreaField('Skills I Can Offer', validators=[Optional()])
    skills_wanted = TextAreaField('Skills I Want to Learn', validators=[Optional()])
    availability = SelectField('Availability', choices=[
        ('', 'Select your availability'),
        ('weekdays', 'Weekdays'),
        ('weekends', 'Weekends'),
        ('evenings', 'Evenings'),
        ('flexible', 'Flexible')
    ], validators=[Optional()])
    is_public = BooleanField('Make my profile public')
    profile_photo = FileField('Profile Photo')
