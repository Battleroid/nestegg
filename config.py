import os

class Config(object):
    SQLALCHEMY_DATABASE_URI = 'mysql://nestegg:nestegg@localhost/nestegg'
    RECAPTCHA_PUBLIC_KEY = '6LfrqAETAAAAAO_BbffXgjLZJ_iEOHNgGBy5Jo2z'
    RECAPTCHA_PRIVATE_KEY = '6LfrqAETAAAAABe7HiBUZAMy9M-lp7kunMwp42eB'
    IMAGES = set(['jpg', 'jpeg', 'png', 'gif'])
    MAX_FREE_FILE_SIZE = 3 * 1024 * 1024
    MAX_PRO_FILE_SIZE = 6 * 1024 * 1024
    TESTING = False
    DEBUG = False
    UPLOAD_DIRECTORY = 'files'

class Development(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = os.urandom(64)

class Testing(Config):
    SECRET_KEY = os.urandom(64)
    TESTING = True

