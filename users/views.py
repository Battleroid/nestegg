from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import logout_user, login_required, login_user
from sqlalchemy import exc
from .forms import LoginForm, RegisterForm
from models import User
from nestegg import db

users_blueprint = Blueprint(
    'users', __name__,
    template_folder='templates'
)

@users_blueprint.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    pass

@users_blueprint.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    pass

@users_blueprint.route('/profile')
def profile():
    pass

@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash('Welcome back, %s.' % user.username)
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form, title='Login')

@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye')
    return redirect(url_for('public.index'))

@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('public.index'))
        except exc.SQLAlchemyError:
            flash('Username or email in use.', 'error')
    else:
        flash('Errors in form', 'error')
    return render_template('register.html', form=form, title='Register')
