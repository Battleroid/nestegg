from flask import render_template, Blueprint
from sqlalchemy import func
from models import File

public_blueprint = Blueprint(
    'public', __name__,
    template_folder='templates'
)

@public_blueprint.route('/tos')
def tos():
    """
    Return static Terms of Service page.
    """
    return 'tos'

@public_blueprint.route('/privacy')
def privacy():
    """
    Return static Privacy Policy.
    """
    return 'privacy policy'

@public_blueprint.route('/about')
def about():
    """
    Return static About page.
    """
    return 'about'

@public_blueprint.route('/')
def index():
    """
    Return home page, as well as a single random photo to be used as the background image.
    """
    samples = File.query.with_entities(File.id, File.name, File.filename).filter(File.public == True).order_by(func.random()).limit(1)
    return render_template('index.html', title='Home', samples=samples)
