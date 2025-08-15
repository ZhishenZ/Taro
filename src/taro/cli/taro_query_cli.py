import argparse
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional

from taro.cli.sub_cli import SubCli
from taro.utils import get_database_url
import taro.db.models as models


def query_ticker_data(ticker: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Query ticker data from the database and return as a pandas DataFrame.

    :param ticker: Stock ticker symbol (e.g., 'GOOGL')
    :param start_date: Optional start date filter (YYYY-MM-DD)
    :param end_date: Optional end date filter (YYYY-MM-DD)
    :return: DataFrame with columns: trade_date, open_price, high_price, low_price, close_price, volume
             Returns None if ticker not found or no data available
    """
    # Create database connection
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if company exists
        company = session.query(models.Company).filter(
            models.Company.company_ticker == ticker
        ).first()

        if company is None:
            return None

        # Build query joining all necessary tables
        query = (
            session.query(
                models.TradeDate.trade_date,
                models.Fundamentals.open_price,
                models.Fundamentals.high_price,
                models.Fundamentals.low_price,
                models.Fundamentals.close_price,
                models.Fundamentals.volume
            )
            .join(models.DailyMetrics, models.DailyMetrics.trade_date_id == models.TradeDate.trade_date_id)
            .join(models.Fundamentals, models.Fundamentals.daily_metrics_id == models.DailyMetrics.id)
            .join(models.Company, models.Company.company_id == models.DailyMetrics.company_id)
            .filter(models.Company.company_ticker == ticker)
        )

        # Apply date filters if provided
        if start_date:
            query = query.filter(models.TradeDate.trade_date >= start_date)
        if end_date:
            query = query.filter(models.TradeDate.trade_date <= end_date)

        # Order by date
        query = query.order_by(models.TradeDate.trade_date)

        # Execute query and fetch results
        results = query.all()

        if not results:
            return None

        # Convert to pandas DataFrame
        df = pd.DataFrame(results, columns=[
            'trade_date',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'volume'
        ])

        # Convert numeric columns to appropriate types
        df['open_price'] = pd.to_numeric(df['open_price'])
        df['high_price'] = pd.to_numeric(df['high_price'])
        df['low_price'] = pd.to_numeric(df['low_price'])
        df['close_price'] = pd.to_numeric(df['close_price'])
        df['volume'] = pd.to_numeric(df['volume'], downcast='integer')

        return df

    finally:
        session.close()


class TaroQueryCli(SubCli):
    def get_name(self):
        return "query"

    def populate_subparser(self, subparser: argparse.ArgumentParser):
        subparser.add_argument("-t", "--ticker", required=True, help="Stock ticker symbol (e.g., GOOGL)")
        subparser.add_argument("-s", "--start", help="Start date (YYYY-MM-DD). Optional filter")
        subparser.add_argument("-e", "--end", help="End date (YYYY-MM-DD). Optional filter")
        subparser.add_argument("-o", "--output", help="Output CSV file path. If not provided, prints to console")
        subparser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output including full table and statistics")

    def run(self, ag):
        ticker = ag.ticker

        # Use the extracted query function
        df = query_ticker_data(ticker, ag.start, ag.end)

        if df is None:
            print(f"Error: Ticker '{ticker}' not found in database or no data available.")
            print(f"Please run backfill first: taro backfill -t {ticker}")
            return

        if len(df) == 0:
            print(f"No data found for ticker '{ticker}'")
            if ag.start or ag.end:
                print(f"Date range: {ag.start or 'earliest'} to {ag.end or 'latest'}")
            return

        # Output results
        if ag.output:
            # Save to CSV file
            df.to_csv(ag.output, index=False)
            print(f"Data saved to {ag.output}")
            print(f"Total records: {len(df)}")

            # Show preview if verbose
            if ag.verbose:
                print(f"\nFirst few rows:")
                print(df.head(10).to_string(index=False))
                print(f"\nSummary statistics:")
                print(df.describe())
        else:
            # Print to console
            if ag.verbose:
                # Verbose mode: show full table and statistics
                print(f"\nData for {ticker}:")
                print("=" * 80)
                print(df.to_string(index=False))
                print("=" * 80)
                print(f"Total records: {len(df)}")
                print(f"\nSummary statistics:")
                print(df.describe())
            else:
                # Non-verbose mode: show summary only
                print(f"\nData for {ticker}:")
                print(f"Total records: {len(df)}")
                print(f"Date range: {df['trade_date'].min()} to {df['trade_date'].max()}")
                print(f"\nFirst 5 rows:")
                print(df.head(5).to_string(index=False))
                print(f"\nLast 5 rows:")
                print(df.tail(5).to_string(index=False))
                print(f"\nUse --verbose flag to see full table and statistics")
