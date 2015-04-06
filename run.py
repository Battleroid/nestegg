import os
import click
from flask_debugtoolbar import DebugToolbarExtension
from nestegg import db, app

def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

@click.group()
def main():
    pass

@main.command()
@click.argument('config', default='dev', type=click.Choice(['dev', 'test', 'prod']))
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=5000)
def run(config, host, port):
    """Start Nestegg with specified configuration."""
    c = {'dev': 'Development', 'testing': 'Testing', 'prod': 'Production'}
    app.config.from_object('config.%s' % c[config])
    dbg = DebugToolbarExtension(app)
    app.run(host=host, port=port)

@main.command()
@click.option('--yes', is_flag=True, expose_value=False, callback=abort_if_false, prompt='Are you sure you want to remove all static files?', help='Do not prompt for removal.')
@click.option('--remove-directory', is_flag=True, help='Remove directory after finishing.')
def clear_dirs(remove_directory):
    """Clear required directories for file storage."""
    app.config.from_object('config.Config')
    if os.path.exists(app.config['UPLOAD_DIRECTORY']):
        for f in os.listdir(app.config['UPLOAD_DIRECTORY']):
            fp = os.path.join(app.config['UPLOAD_DIRECTORY'], f)
            try:
                if os.path.isfile(fp):
                    os.unlink(fp)
            except Exception, e:
                print e
    if remove_directory:
        os.rmdir(app.config['UPLOAD_DIRECTORY'])

@main.command()
def setup_dirs():
    """Create required directories to store files."""
    app.config.from_object('config.Config')
    path = os.path.join(app.config['UPLOAD_DIRECTORY'])
    if not os.path.exists(path):
        os.mkdir(path)

@main.command()
@click.option('--yes', is_flag=True, expose_value=False, callback=abort_if_false, prompt='Are you sure you want to reset the database?', help='Do not prompt for reset.')
def reset():
    """Reset Nestegg database."""
    app.config.from_object('config.Config')
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    main()
