import argparse
import os

from taro.cli.sub_cli import SubCli
from taro.cli.taro_query_cli import query_ticker_data


from threading import Thread

from flask import Flask, render_template, request
from tornado.ioloop import IOLoop

from bokeh.embed import server_document
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput, Button, Div
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
import pandas as pd


app = Flask(__name__)

ec2_host = os.getenv('EC2_HOST', 'localhost')

# Default ticker
DEFAULT_TICKER = "GOOGL"

def bkapp(doc):
    # Query initial data
    df = query_ticker_data(DEFAULT_TICKER)

    if df is None or len(df) == 0:
        # If no data, create empty dataframe
        df = pd.DataFrame(columns=['trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])

    # Convert trade_date to datetime for plotting
    df['trade_date'] = pd.to_datetime(df['trade_date'])

    source = ColumnDataSource(data=df)
    original_df = df.copy()

    # Create price plot
    price_plot = figure(
        x_axis_type='datetime',
        y_axis_label='Price ($)',
        title=f"Stock Price for {DEFAULT_TICKER}",
        width=1000,
        height=400
    )

    price_plot.line('trade_date', 'close_price', source=source, legend_label='Close', color='blue', line_width=2)
    price_plot.line('trade_date', 'open_price', source=source, legend_label='Open', color='green', line_width=1, alpha=0.7)
    price_plot.line('trade_date', 'high_price', source=source, legend_label='High', color='red', line_width=1, alpha=0.5)
    price_plot.line('trade_date', 'low_price', source=source, legend_label='Low', color='orange', line_width=1, alpha=0.5)

    price_plot.legend.location = "top_left"
    price_plot.legend.click_policy = "hide"

    # Create volume plot
    volume_plot = figure(
        x_axis_type='datetime',
        y_axis_label='Volume',
        title=f"Trading Volume for {DEFAULT_TICKER}",
        width=1000,
        height=200,
        x_range=price_plot.x_range  # Link x-axis with price plot
    )

    volume_plot.vbar(x='trade_date', top='volume', source=source, width=pd.Timedelta(days=0.8), color='navy', alpha=0.5)

    # Smoothing slider
    def smoothing_callback(attr, old, new):
        if new == 0:
            data = original_df
        else:
            data = original_df.copy()
            for col in ['open_price', 'high_price', 'low_price', 'close_price', 'volume']:
                data[col] = data[col].rolling(window=new, min_periods=1).mean()
        source.data = ColumnDataSource.from_df(data)

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days", width=400)
    slider.on_change('value', smoothing_callback)

    # Ticker input
    ticker_input = TextInput(value=DEFAULT_TICKER, title="Ticker Symbol:", width=200)

    # Status message
    status_div = Div(text="", width=600, height=30)

    def update_ticker():
        nonlocal original_df
        ticker = ticker_input.value.upper()

        # Query new data
        new_df = query_ticker_data(ticker)

        if new_df is None or len(new_df) == 0:
            status_div.text = f'<p style="color: red;">No data found for ticker: {ticker}</p>'
            return

        # Convert trade_date to datetime
        new_df['trade_date'] = pd.to_datetime(new_df['trade_date'])

        # Update data
        original_df = new_df.copy()
        source.data = ColumnDataSource.from_df(new_df)

        # Update titles
        price_plot.title.text = f"Stock Price for {ticker}"
        volume_plot.title.text = f"Trading Volume for {ticker}"

        # Reset slider
        slider.value = 0

        status_div.text = f'<p style="color: green;">Successfully loaded data for {ticker} ({len(new_df)} records)</p>'

    update_button = Button(label="Load Ticker", button_type="success", width=150)
    update_button.on_click(update_ticker)

    # Layout
    controls = row(ticker_input, update_button, slider)
    layout = column(controls, status_div, price_plot, volume_plot)

    doc.add_root(layout)

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
