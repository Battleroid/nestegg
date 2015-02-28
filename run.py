import click
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
    app.run(host=host, port=port)

@main.command()
@click.option('--yes', is_flag=True, expose_value=False, callback=abort_if_false, prompt='Are you sure you want to reset the database?')
def reset():
    """Reset Nestegg database."""
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    main()
