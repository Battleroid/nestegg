import os, datetime, humanize, stripe, stripe_keys
from flask import render_template, Blueprint, request, flash, redirect, url_for, Response, g
from flask_login import logout_user, login_required, login_user, current_user
from sqlalchemy import exc
from users.forms import LoginForm, RegisterForm, UploadForm, EditProfile, PasswordForm, EditPhotoForm, Search
from models import User, File
from nestegg import app, db
from util import flash_errors, allowed_filename

users_blueprint = Blueprint(
    'users', __name__,
    template_folder='templates',
    url_prefix='/user'
)

@users_blueprint.before_request
def before_request():
    g.user = current_user
    g.user.search_form = Search()

stripe.api_key = stripe_keys.secret

def update_sub(stripe_customer_id, end_date):
    """
    Updates the subscription status and end date for a particular customer based on stripe ID.

    :param str stripe_customer_id: Stripe customer ID
    :param DateTime end_date: End date object for customer subscription
    """
    user = User.query.filter_by(stripe_token=stripe_customer_id).first()
    timestamp = datetime.datetime.fromtimestamp(end_date)
    print user
    if not user:
        return
    user.pro_expiration = timestamp
    user.pro_status = True
    db.session.commit()

def cancel_sub(stripe_customer_id, end_date):
    """
    Cancel subscription for user matching Stripe ID and move end date for subscription status.

    :param str stripe_customer_id: stripe ID
    :param DateTime end_date: end date DateTime object
    """
    user = User.query.filter_by(stripe_token=stripe_customer_id).first()
    timestamp = datetime.datetime.fromtimestamp(end_date)
    if not user:
        return
    user.pro_expiration = timestamp
    user.pro_status = False
    db.session.commit()

@users_blueprint.route('/hook/', methods=['POST'])
def hook():
    """
    Receive webhooks from Stripe for subscription events.
    """
    if not request.json or not request.json.get('id'):
        return Response(status=406)
    payload = request.json
    event = stripe.Event.retrieve(payload.get('id'))
    if event.type == 'customer.subscription.deleted':
        cancel_sub(event.data.object.customer, event.data.object.ended_at)
    elif event.type == 'customer.subscription.updated':
        update_sub(event.data.object.customer, event.current_period_end)
    return Response(status=200)

@users_blueprint.route('/unsubscribe', methods=['GET'])
@login_required
def unsubscribe():
    """
    Unsubscribe current user using stripe ID from database.

    :param str stripe_token: stripe ID
    """
    if not current_user.pro_status:
        flash('You cannot unsubscribe unless you have a subscription.', 'error')
        return redirect(url_for('users.control_panel'))
    customer = stripe.Customer.retrieve(current_user.stripe_token)
    customer.cancel_subscription()
    current_user.pro_status = False
    current_user.pro_expiration = datetime.datetime.now()
    db.session.commit()
    flash('You have been successfully unsubscribed.', 'good')
    return redirect(url_for('users.control_panel'))

@users_blueprint.route('/pro', methods=['GET', 'POST'])
@login_required
def pro():
    """
    Allow user to manage their subscription. This includes both signing up for a subscription and removing it.

    :form stripeToken: token from Stripe.js
    :form stripeEmail: email address for customer
    """
    if request.method == 'POST' and current_user.pro_status:
        flash('Cannot subscribe if already a subscriber.', 'error')
        return redirect(url_for('users.control_panel'))
    if request.method == 'POST':
        try:
            cus_token = request.form['stripeToken']
            cus_email = request.form['stripeEmail']
            cus = stripe.Customer.create(
                source=cus_token,
                plan="pro",
                email=cus_email
            )
            current_user.stripe_token = cus.id
            current_user.pro_status = True
            current_user.pro_expiration = datetime.datetime.fromtimestamp(cus.subscriptions.data[0].current_period_end)
            db.session.commit()
        except stripe.CardError, e:
            flash('Could not charge your card, please check the card details or contact your card issuer.', 'error')
    return render_template('pro.html', title='Pro Information', public_key=stripe_keys.public)

@users_blueprint.route('/control-panel', methods=['GET', 'POST'])
@login_required
def control_panel():
    """
    Display basic control panel for user.
    """
    return render_template('control_panel.html', title='Control Panel')

@users_blueprint.route('/photo/<int:photo_id>')
def view_photo(photo_id):
    """
    View the specified photo.

    :param int photo_id: photo ID
    """
    photo = File.query.filter(File.id == photo_id).first()
    if not photo_id or not photo:
        flash('Photo does not exist!', 'error')
        if current_user:
            return redirect(url_for('users.control_panel'))
        else:
            return redirect(url_for('public.index'))
    owner = User.query.with_entities(User.username).filter(User.id == photo.user_id).first()
    return render_template('view_photo.html', title=photo.name, photo=photo, owner=owner)

@users_blueprint.route('/<username>/gallery')
@users_blueprint.route('/<username>/gallery/<int:page>')
def public_gallery(username, page=1):
    """
    Public paginated gallery for user.

    :param str username: username
    :param int page: page number
    """
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('public.index'))
    if current_user.is_anonymous() or not current_user.pro_status:
        query = user.files.filter(File.public == True).with_entities(File.id, File.name, File.filename)
    else:
        query = user.files.with_entities(File.id, File.name, File.filename)
    photos = query.paginate(page, 12, False)
    return render_template('public_gallery.html', title='%s\'s Photos' % user.username.capitalize(), user=user.username, photos=photos)

@users_blueprint.route('/gallery/')
@users_blueprint.route('/gallery/<int:page>')
@login_required
def gallery(page=1):
    """
    Personal gallery for user wherein they can delete and edit photos.

    :param int page: page number
    """
    photos = current_user.files.with_entities(File.id, File.name, File.filename).paginate(page, 12, False)
    return render_template('gallery.html', title='Your Photos', photos=photos)

@users_blueprint.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """
    Upload file given information from form.

    :form photo: file to be uploaded
    :form title: title
    :form desc: description
    """
    form = UploadForm()
    if current_user.pro_status == 0:
        if current_user.files.count() > 20:
            flash('You need a subscription to upload more than 20 files!', 'error')
            return redirect(url_for('users.control_panel'))
    if request.method == 'POST' and form.validate_on_submit():
        if allowed_filename(form.photo.data.filename):
            # f_size = len(form.photo.data.stream.read()) for file size  # implement at later date, for now we'll just deal with it
            f = File(form.title.data, form.desc.data, form.photo.data.filename.rsplit('.')[-1])  # incorrect .rsplit, fix
            form.photo.data.save(os.path.join(app.config['UPLOAD_DIRECTORY'], f.filename))
            current_user.files.append(f)
            db.session.add(f)
            db.session.commit()
            flash('File %s uploaded!' % f.name, 'good')
            return redirect(url_for('users.control_panel'))
        else:
            flash('File is not a valid type.', 'error')
    else:
        flash_errors(form)
    return render_template('upload.html', title='Upload File', form=form)

@users_blueprint.route('/edit-profile/about', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Edit basic information for user profile.

    :form first_name: first name of user
    :form last_name: last name of user
    """
    form = EditProfile(obj=current_user)
    if request.method == 'POST' and form.validate_on_submit():
        current_user.first_name = form.first_name.data if form.first_name.data else current_user.first_name
        current_user.last_name = form.last_name.data if form.last_name.data else current_user.last_name
        current_user.about = form.about.data if form.about.data else current_user.about
        db.session.commit()
        flash('Changes saved.', 'good')
    else:
        flash_errors(form)
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@users_blueprint.route('/edit-profile/security', methods=['GET', 'POST'])
@login_required
def edit_security():
    """
    Edit password for user.

    :form current_password: current password for user
    :form password: new password for user
    :form confirm: new password confirmation
    """
    form = PasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.password = form.password.data
            db.session.commit()
            flash('Changes saved.', 'good')
        else:
            flash('Current password is incorrect.', 'error')
    else:
        flash_errors(form)
    return render_template('edit_security.html', title='Change Password', form=form)

@users_blueprint.route('/view-profile/<username>')
def view_profile(username):
    """
    Present public profile of user.
    
    :param str username: username
    """
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', title='Public Profile of ' + user.username, user=user)

@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login user using credentials from form.

    :form username: username
    :form password: password
    """
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Welcome back, %s.' % user.username)
            return redirect(request.args.get('next') or url_for('users.control_panel'))
        else:
            flash('Invalid username or password.', 'error')
    else:
        flash_errors(form)
    return render_template('login.html', form=form, title='Login')

@users_blueprint.route('/logout')
@login_required
def logout():
    """
    Logout the current user.
    """
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('public.index'))

@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register user based on form parameters.

    :form username: username
    :form password: password
    :form email: email address for user
    """
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
        flash_errors(form)
    return render_template('register.html', form=form, title='Register')

@users_blueprint.route('/remove-photo/<int:image_id>', methods=['GET'])
@login_required
def remove_photo(image_id):
    """
    Delete image ID if image belongs to current user.

    :param int image_id: image ID
    """
    if not image_id or not current_user.files.filter(File.id == image_id).first():
        flash('That image does not exist.', 'error')
        return redirect(url_for('users.control_panel'))  # for now redirect to CP, as gallery is not functional yet
    photo = File.query.get(image_id)
    photo_path = os.path.join(app.config['UPLOAD_DIRECTORY'], photo.filename)
    if os.path.exists(photo_path):
        os.remove(photo_path)
    db.session.delete(photo)
    db.session.commit()
    flash('Photo removed.', 'good')
    if current_user.files.count() > 0:
        return redirect(url_for('users.gallery'))
    else:
        return redirect(url_for('users.control_panel'))

@users_blueprint.route('/edit-photo/<int:image_id>', methods=['GET', 'POST'])
@login_required
def edit_photo(image_id):
    """
    Edit image properties, including title and description.

    :param int image_id: image ID
    """
    if not image_id or not current_user.files.filter(File.id == image_id).first():
        flash('That image does not exist.', 'error')
        return redirect(url_for('users.control_panel'))
    photo = File.query.get(image_id)
    form = EditPhotoForm(obj=photo)
    if request.method == 'POST' and form.validate_on_submit():
        if current_user.pro_status:
            photo.public = form.public.data
        photo.name = form.name.data if form.name.data else photo.name
        photo.desc = form.desc.data if form.desc.data else photo.desc
        db.session.commit()
        flash('Changes saved!', 'good')
    return render_template('edit_photo.html', title='Edit Photo', form=form, image_id=image_id)

@users_blueprint.route('/search', methods=['POST'])
def search():
    """
    Initiate search based on whether or not search form parameters are validated.
    """
    if not g.search_form.validate_on_submit():
        return redirect(url_for('public.index'))
    return redirect(url_for('users.search_results', query=g.search_form.search_term.data))

@users_blueprint.route('/search_results/<query>')
@users_blueprint.route('/search_results/<query>/<int:page>')
def search_results(query, page=1):
    """
    Return paginated search results.

    :param str query: search terms
    :param int page: page number
    """
    search = File.query.whoosh_search(query)
    results = search.paginate(page, 12, False)
    return render_template('search.html', title='Results for %s' % query, query=query, photos=results)

@users_blueprint.app_template_filter()
def timesince(z):
    """
    Return a human readable time in format of when the post was made.
    """
    return humanize.naturaltime(z)

@users_blueprint.app_template_filter()
def datetimeformat(z, format='%Y-%m-%d'):
    """
    Format time in short date format.
    """
    return z.strftime(format)
