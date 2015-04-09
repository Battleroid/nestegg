from flask import render_template, Blueprint
from sqlalchemy import func
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
    samples = File.query.with_entities(File.id, File.name, File.filename).filter(File.public == True).order_by(func.random()).limit(1)
    return render_template('index.html', title='Home', samples=samples)
