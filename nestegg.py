from flask_sqlalchemy import SQLAlchemy
from flask_compress import Compress
from flask_bcrypt import Bcrypt
from flask_cache import Cache
from flask_login import LoginManager
from flask import Flask, render_template

# Flask
app = Flask(__name__)

# ORM
db = SQLAlchemy(app)

# Bcrypt
bc = Bcrypt(app)

# Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

# Login Manager
lm = LoginManager()
lm.init_app(app)

# Compress
compress = Compress(app)

# Blueprints
from public.views import public_blueprint
from users.views import users_blueprint
app.register_blueprint(public_blueprint)
app.register_blueprint(users_blueprint)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', error=e)

@app.errorhandler(500)
def server_error(e):
    return render_template('50x.html', error=e)

# Setup Login Manager
from models import User

lm.login_view = 'users.login'

@lm.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()
