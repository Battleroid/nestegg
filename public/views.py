from flask import render_template, Blueprint
from models import File

public_blueprint = Blueprint(
    'public', __name__,
    template_folder='templates'
)

@public_blueprint.route('/tos')
def tos():
    pass

@public_blueprint.route('/privacy')
def privacy():
    pass

@public_blueprint.route('/about')
def about():
    pass

@public_blueprint.route('/')
def index():
    gallery = File.query.limit(10).all()
    return render_template('index.html', title='Home', gallery=gallery)
