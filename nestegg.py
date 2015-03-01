from flask.ext.uploads import configure_uploads, IMAGES, UploadSet
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cache import Cache
from flask_login import LoginManager
from flask_assets import Environment, Bundle
from flask import Flask, render_template

# Flask
app = Flask(__name__)

# ORM
db = SQLAlchemy(app)

# Bcrypt
bc = Bcrypt(app)

# Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

# Assets
assets = Environment(app)
css = Bundle('main.css', 'normalize.css', 'skeleton.css', filters='cssmin', output='min/default.css')
assets.register('css_min', css)

# Login Manager
lm = LoginManager()
lm.init_app(app)

# Blueprints
from public.views import public_blueprint
from users.views import users_blueprint
app.register_blueprint(public_blueprint)
app.register_blueprint(users_blueprint)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', error=e)

@app.errorhandler(501)
@app.errorhandler(502)
@app.errorhandler(503)
@app.errorhandler(500)
def server_error(e):
    return render_template('50x.html', error=e)

# Setup Login Manager
from models import User

lm.login_view = 'users.login'

@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)
