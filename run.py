from nestegg import app
import os

if __name__ == '__main__':
    app.config['SECRET_KEY'] = os.urandom(32)
    app.run(host='0.0.0.0', debug=True)
