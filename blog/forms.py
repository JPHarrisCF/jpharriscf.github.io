from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from blog.models import User


class RegistrationForm(FlaskForm):
    firstname= StringField('FIRST NAME', validators=[DataRequired(), Length(min=1, max=30)], render_kw = {'placeholder': 'Enter your first name'})
    surname= StringField('SURNAME', validators=[DataRequired(), Length(min=1, max=30)], render_kw = {'placeholder': 'Enter your surname'})
    username = StringField('CHOSEN USERNAME', validators=[DataRequired(), Length(min=3, max=15, message="Your username should be between 3 and 15 characters.")], render_kw = {'placeholder': 'Enter a Username'})
    email = StringField('EMAIL', validators=[DataRequired(), Email()], render_kw = {'placeholder': 'Enter a valid e-mail'})
    password = PasswordField('PASSWORD', validators=[DataRequired(), Regexp('^.{3,12}$', message='Your password should be between 3 and 12 characters long.')], render_kw = {'placeholder': 'Enter a password'})
    confirm_password = PasswordField('CONFIRM PASSWORD', validators=[DataRequired(), EqualTo('password', message='Passwords do not match.')], render_kw = {'placeholder': 'Confirm your password'})
    submit = SubmitField('REGISTER')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose another.')

    def validate_email(self, email):    
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists. Please choose another.')

class LoginForm(FlaskForm):
    email = StringField('EMAIL', validators=[DataRequired()])
    password = PasswordField('PASSWORD', validators=[DataRequired()])
    submit = SubmitField('LOGIN')

class CommentForm(FlaskForm):
    comment = StringField('COMMENT', validators=[InputRequired()])
    submit = SubmitField('POST COMMENT')

class LikeForm(FlaskForm):
    submit = SubmitField('LIKE POST')

class UnlikeForm(FlaskForm):
    submit = SubmitField('UNLIKE POST')

class SavedPostForm(FlaskForm):
    submit = SubmitField('SAVE POST')

class ForgetPostForm(FlaskForm):
    submit = SubmitField('FORGET POST')