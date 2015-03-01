from distutils.core import setup

setup(
    name='nestegg',
    version='0.1',
    packages=['users', 'public'],
    url='https://github.com/battleroid/nestegg',
    license='',
    author='Casey Weed',
    author_email='casweed@gmail.com',
    description='E-Commerce project.',
    install_requires=[
        'Flask=0.10.1',
        'Flask-Assets=0.10',
        'Flask-Bcrypt=0.6.0',
        'Flask-Cache=0.13.1',
        'Flask-DebugToolbar=0.9.1',
        'Flask-Login=0.2.11',
        'Flask-SQLAlchemy=2.0',
        'Flask-Session=0.1.1',
        'Flask-User=0.6.1',
        'Jinja2=2.7.3',
        'redis=2.10.3',
        'itsdangerous=0.24',
        'click=3.3'
    ]
)
