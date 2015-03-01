from nestegg import app
from models import File
from os.path import join

UPLOAD_DIRECTORY = app.config['UPLOAD_DIRECTORY']
IMAGES = app.config['IMAGES']
MAX_FREE_FILE_SIZE = app.config['MAX_FREE_FILE_SIZE']
MAX_PRO_FILE_SIZE = app.config['MAX_PRO_FILE_SIZE']

def handle_upload(form, pro=False):
    size = MAX_PRO_FILE_SIZE if pro else MAX_FREE_FILE_SIZE
    ext = form.photo.data.filename.split('.')[-1]
    f = File(form.title.data, form.desc.data, ext)