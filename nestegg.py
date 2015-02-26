from flask_sqlalchemy import SQLAlchemy
from flask_compress import Compress
from flask_bcrypt import Bcrypt
from flask_cache import Cache
from flask_login import LoginManager
from flask import Flask

# Flask
app = Flask(__name__)
app.config.from_pyfile('config.py')

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

from models import User

lm.login_view = 'users.login'
@lm.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()
