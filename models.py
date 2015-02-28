import datetime
from uuid import uuid4
from sqlalchemy.ext.hybrid import hybrid_property
from nestegg import db, bc

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    _pw = db.Column('password', db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    about = db.Column(db.Text(1000))
    registered_at = db.Column(db.DateTime, default=datetime.datetime.now())
    stripe_token = db.Column(db.String(255), nullable=True, unique=True)
    pro_status = db.Column(db.Boolean, server_default='0')
    pro_expiration = db.Column(db.DateTime, nullable=True)
    files = db.relationship('File', backref='user', lazy='dynamic')

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def check_password(self, value):
        return bc.check_password_hash(self._pw, value)

    @hybrid_property
    def password(self):
        return self._pw

    @password.setter
    def set_password(self, plain):
        self._pw = bc.generate_password_hash(plain)

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r %r>' % (self.username, self.email)


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text(512), nullable=True)

    def __init__(self, name, desc, extension):
        self.name = name
        self.desc = desc
        self.filename = self.generate_filename(extension)

    def __repr__(self):
        return '<File %r %r>' % (self.name, self.filename)

    def generate_filename(self, extension):
        name = uuid4().hex + "." + extension
        while File.query.filter_by(filename=name).first():
            name = uuid4().hex + "." + extension
        return name
