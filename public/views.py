from flask import render_template, Blueprint
from models import File

public_blueprint = Blueprint(
    'public', __name__,
    template_folder='templates'
)

@public_blueprint.route('/tos')
def tos():
    return 'tos'

@public_blueprint.route('/privacy')
def privacy():
    return 'privacy policy'

@public_blueprint.route('/about')
def about():
    return 'about'

@public_blueprint.route('/')
def index():
    gallery = File.query.limit(5).all()
    return render_template('index.html', title='Home', gallery=gallery)
