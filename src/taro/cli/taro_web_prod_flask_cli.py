import argparse
import os

from taro.cli.sub_cli import SubCli

from flask import Flask, render_template
from bokeh.embed import server_document


app = Flask(__name__)

ec2_host = os.getenv('EC2_HOST', 'localhost')

@app.route('/', methods=['GET'])
def bkapp_page():
    # Use HTTPS in production if not localhost
    if ec2_host in ['localhost', '127.0.0.1']:
        # Local development: connect directly to port 5006
        script = server_document(f'http://{ec2_host}:5006/bkapp')
    else:
        # Production: Traefik proxies /bkapp to port 5006
        script = server_document(f'https://{ec2_host}/bkapp')

    return render_template("embed.html", script=script, template="Flask")

class TaroWebProdFlaskCli(SubCli):
    def get_name(self):
        return "web-prod"

    def populate_subparser(self, subparser:argparse.ArgumentParser):
        subparser.add_argument("--port", type=int, default=5000, help="Port to run the server on (default: 5000)")
        subparser.add_argument("--workers", type=int, default=1, help="Number of Gunicorn workers (default: 1)")

    def run(self, ag):
        print(f'Starting production Flask app with Gunicorn')
        print(f'Access at: http://localhost:{ag.port}/')
        print()

        # Check if gunicorn is available
        try:
            import gunicorn.app.base

            class StandaloneApplication(gunicorn.app.base.BaseApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()

                def load_config(self):
                    for key, value in self.options.items():
                        if key in self.cfg.settings and value is not None:
                            self.cfg.set(key.lower(), value)

                def load(self):
                    return self.application

            options = {
                'bind': f'0.0.0.0:{ag.port}',
                'workers': ag.workers,
                'threads': 2,
                'timeout': 120,
                'accesslog': '-',  # Log to stdout
                'errorlog': '-',   # Log to stderr
                'loglevel': 'info',
            }

            print(f'Using Gunicorn WSGI server with {ag.workers} worker(s)')
            StandaloneApplication(app, options).run()

        except ImportError:
            print('ERROR: Gunicorn is not installed!')
            print('Install it with: pip install gunicorn')
            print()
            print('Falling back to Flask development server...')
            app.run(port=ag.port, host="0.0.0.0")
