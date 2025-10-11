import argparse
import os

from taro.cli.sub_cli import SubCli
from taro.bokeh_figures.price_volumn import bkapp

from tornado.ioloop import IOLoop

from bokeh.server.server import Server


ec2_host = os.getenv('EC2_HOST', 'localhost')


class TaroWebProdBokehCli(SubCli):
    def get_name(self):
        return "bokeh-server"

    def populate_subparser(self, subparser: argparse.ArgumentParser):
        subparser.add_argument("--port", type=int, default=5006, help="Port to run the Bokeh server on (default: 5006)")

    def run(self, ag):
        print(f'Starting Bokeh server on port {ag.port}')
        print(f'Application path: /bkapp')
        print()

        # WebSocket origins: allow domain (proxied through Traefik) and localhost
        origins = [ec2_host, f"{ec2_host}:5006", f"{ec2_host}:5000", "127.0.0.1:5000", "localhost:5000", "127.0.0.1:5006", "localhost:5006"]

        server = Server(
            {'/bkapp': bkapp},
            io_loop=IOLoop(),
            port=ag.port,
            allow_websocket_origin=origins,
            session_token_expiration=86400000  # 24 hours in milliseconds
        )

        server.start()
        server.io_loop.start()
