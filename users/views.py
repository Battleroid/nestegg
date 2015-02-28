import os
from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import logout_user, login_required, login_user, current_user
from sqlalchemy import exc
from .forms import LoginForm, RegisterForm, UploadForm, EditProfile
from models import User, File
import humanize
from nestegg import db

users_blueprint = Blueprint(
    'users', __name__,
    template_folder='templates'
)

@users_blueprint.route('/profile/cp', methods=['GET', 'POST'])
@login_required
def control_panel():
    return render_template('control_panel.html', title='Control Panel')

@users_blueprint.route('/profile/pro', methods=['GET', 'POST'])
@login_required
def pro():
    pass

@users_blueprint.route('/profile/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        f = File(form.title.data, form.desc.data, form.photo.data.rsplit('.')[-1])
        current_user.files.append(f)
        # see: http://stackoverflow.com/questions/27611827/attributeerror-filefield-object-has-no-attribute-file
        # form.photo.file.save(os.path.join(app.config['UPLOADS_DIRECTORY'], f.filename))
        db.session.add(f)
        db.session.commit()
        flash('File %s uploaded!' % f.name)
    return render_template('upload.html', title='Upload File', form=form)

@users_blueprint.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfile()
    if request.method == 'POST' and form.validate_on_submit():
        if current_user.check_password(form.password.data):
            current_user.about = form.about.data
            db.session.commit()
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@users_blueprint.route('/view/profile/<username>')
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', title='Public Profile of ' + user.username, user=user)

@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash('Welcome back, %s.' % user.username)
            # next = request.args.get('next')
            return redirect(url_for('users.control_panel'))
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

@users_blueprint.app_template_filter()
def timesince(z):
    return humanize.naturaltime(z)
