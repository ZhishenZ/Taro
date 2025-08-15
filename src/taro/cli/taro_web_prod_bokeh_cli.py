import argparse
import os

from taro.cli.sub_cli import SubCli
from taro.cli.taro_query_cli import query_ticker_data

from tornado.ioloop import IOLoop

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput, Button, Div
from bokeh.plotting import figure
from bokeh.server.server import Server
import pandas as pd


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
