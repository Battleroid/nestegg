import os
from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import logout_user, login_required, login_user, current_user
from sqlalchemy import exc
from .forms import LoginForm, RegisterForm, UploadForm, EditProfile
from models import User, File
from nestegg import app, db
import humanize

users_blueprint = Blueprint(
    'users', __name__,
    template_folder='templates'
)

@users_blueprint.route('/profile/cp', methods=['GET', 'POST'])
@login_required
def control_panel():
    '''Basic control panel where all user specific configuration options are made available.'''
    return render_template('control_panel.html', title='Control Panel')

@users_blueprint.route('/profile/gallery/')
@users_blueprint.route('/profile/gallery/<int:page>')
@login_required
def gallery(page=1):
    '''Paginated gallery (app.config param for max images per page). From here users can delete photos, possibly edit, make public, etc.'''
    pass

@users_blueprint.route('/profile/pro', methods=['GET', 'POST'])
@login_required
def pro():
    '''Allows user to manage their subscription. This includes removing their subscription (ending it immediately afaik, work with Stripe for delayed end?) and subscribing.'''
    pass

@users_blueprint.route('/profile/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    '''Upload file and attach title/description.'''
    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        # f_size = len(form.photo.data.stream.read()) for file size  # implement at later date, for now we'll just deal with it
        f = File(form.title.data, form.desc.data, form.photo.data.filename.rsplit('.')[-1])  # incorrect .rsplit, fix
        form.photo.data.save(os.path.join(app.config['UPLOAD_DIRECTORY'], f.filename))
        current_user.files.append(f)
        db.session.add(f)
        db.session.commit()
        flash('File %s uploaded!' % f.name)
    return render_template('upload.html', title='Upload File', form=form)

@users_blueprint.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    '''Edit basic information for user, including about, first/last name.'''
    form = EditProfile(obj=current_user)
    if request.method == 'POST' and form.validate_on_submit():
        current_user.first_name = form.first_name.data if form.first_name.data else current_user.first_name
        current_user.last_name = form.last_name.data if form.last_name.data else current_user.last_name
        current_user.about = form.about.data if form.about.data else current_user.about
        db.session.commit()
        flash('Changes saved.')
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@users_blueprint.route('/view/profile/<username>')
def view_profile(username):
    '''Present public profile of user.'''
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
            return redirect(request.args.get('next') or url_for('users.control_panel'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form, title='Login')

@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
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

@users_blueprint.route('/remove/<int:image_id>', methods=['GET'])
def remove_photo(image_id):
    '''Remove photo ID if it exists and belongs to currently logged in user.'''
    if not image_id or not current_user.files.filter(File.id == image_id).first():
        flash('That image does not exist.')
        return redirect(url_for('users.control_panel'))  # for now redirect to CP, as gallery is not functional yet
    photo = File.query.get(image_id)
    photo_path = os.path.join(app.config['UPLOAD_DIRECTORY'], photo.filename)
    if os.path.exists(photo_path):
        os.remove(photo_path)
    db.session.delete(photo)
    db.session.commit()
    flash('Photo removed.')
    # return redirect(url_for('user.gallery'))
    return redirect(url_for('users.control_panel'))

@users_blueprint.app_template_filter()
def timesince(z):
    return humanize.naturaltime(z)
