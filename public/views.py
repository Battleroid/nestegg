from flask import render_template, Blueprint
from models import File

public_blueprint = Blueprint(
    'public', __name__,
    template_folder='templates'
)


@public_blueprint.route('/')
def index():
    gallery = File.query.limit(10).all()
    return render_template('index.html', title='Home', gallery=gallery)
