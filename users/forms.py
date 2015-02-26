from flask_wtf import Form, RecaptchaField
from wtforms.validators import Length, DataRequired, EqualTo, Email
from wtforms import StringField, PasswordField, SubmitField, BooleanField

class LoginForm(Form):
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(Form):
    username = StringField('Username', [DataRequired(), Length(4, 20)])
    password = PasswordField('Password', [DataRequired(), Length(8, 255)])
    confirm = PasswordField('Confirm Password', [DataRequired(), EqualTo('password', 'Passwords must match.')])
    email = StringField('Email Address', [DataRequired(), Email(message=None)])
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign Up')