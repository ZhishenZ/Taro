import argparse
import os

from taro.cli.sub_cli import SubCli
from taro.bokeh_figures.price_volumn import bkapp


from threading import Thread

from flask import Flask, render_template, request
from tornado.ioloop import IOLoop

from bokeh.embed import server_document
from bokeh.server.server import Server


app = Flask(__name__)

ec2_host = os.getenv('EC2_HOST', 'localhost')

@app.route('/', methods=['GET'])
def bkapp_page():
    script = server_document(f'http://{ec2_host}:5006/bkapp')
    from pathlib import Path
    filepath = Path(__file__)

    return render_template("embed.html", script=script, template="Flask")

def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server(
        {'/bkapp': bkapp},
        io_loop=IOLoop(),
        allow_websocket_origin=[f"{ec2_host}:5000", f"127.0.0.1:5000", f"localhost:5000"],
        session_token_expiration=86400000  # 24 hours in milliseconds
    )
    server.start()
    server.io_loop.start()

class TaroWebCli(SubCli):
    def get_name(self):
        return "web"

    def populate_subparser(self, subparser:argparse.ArgumentParser):
        # subparser.add_argument("-e", "--ec2_host", default="localhost")
        pass

    def run(self, ag):

        Thread(target=bk_worker).start()

        print('Opening single process Flask app with embedded Bokeh application on http://localhost:8000/')
        print()
        print('Multiple connections may block the Bokeh app in this configuration!')
        print('See "flask_gunicorn_embed.py" for one way to run multi-process')
        app.run(port=5000, host="0.0.0.0")


# export BOKEH_ALLOW_WS_ORIGIN=127.0.0.1:8000
