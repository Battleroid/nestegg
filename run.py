from nestegg import app
from flask_debugtoolbar import DebugToolbarExtension

if __name__ == '__main__':
    app.config.from_object('config.Development')
    toolbar = DebugToolbarExtension(app)
    app.run(host='0.0.0.0')
