from flask_wtf import Form, RecaptchaField
from flask_wtf.html5 import EmailField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import Length, DataRequired, EqualTo, Email, Optional, InputRequired
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField

class LoginForm(Form):
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField('Remember Me?', [Optional()])
    submit = SubmitField('Login')

class RegisterForm(Form):
    username = StringField('Username', [DataRequired(), Length(4, 20)])
    password = PasswordField('Password', [DataRequired(), Length(8, 255)])
    confirm = PasswordField('Confirm Password', [DataRequired(), EqualTo('password', 'Passwords must match.')])
    email = StringField('Email Address', [DataRequired(), Email(message='Not a valid email.')])
    agree_to_tos = BooleanField('I agree to the Terms of Service', [InputRequired()])
    # recaptcha = RecaptchaField()  # disable temporarily while in development
    submit = SubmitField('Sign Up')

class UploadForm(Form):
    photo = FileField('Photo', [FileRequired('You need to upload an image!')])
    title = StringField('Title', [DataRequired(), Length(1, 255)])
    desc = TextAreaField('Description (optional)', [Optional()])
    submit = SubmitField('Upload')

class PasswordForm(Form):
    current_password = PasswordField('Current Password', [DataRequired(), Length(8, 255)])
    password = PasswordField('Password', [DataRequired(), Length(8, 255)])
    confirm = PasswordField('Confirm Password', [DataRequired(), EqualTo('password', 'Passwords must match.')])
    submit = SubmitField('Change Password')

class EditProfile(Form):
    first_name = StringField('First name', [Optional(), Length(max=50)])
    last_name = StringField('Last name', [Optional(), Length(max=50)])
    about = TextAreaField('About Me', [Optional(), Length(max=512)])
    submit = SubmitField('Save Changes')