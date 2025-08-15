import argparse
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from taro.cli.sub_cli import SubCli
from taro.utils import get_database_url
from taro.fetcher.fetcher_yfinance import YFinanceFetcher
import taro.db.models as models


class TaroBackfillCli(SubCli):
    def get_name(self):
        return "backfill"

    def populate_subparser(self, subparser: argparse.ArgumentParser):
        subparser.add_argument("-t", "--ticker", required=True, help="Stock ticker symbol (e.g., GOOGL)")
        subparser.add_argument("-s", "--start", help="Start date (YYYY-MM-DD). Default: earliest available date for ticker")
        subparser.add_argument("-e", "--end", help="End date (YYYY-MM-DD). Default: yesterday")

    def update_database(self, ticker, date, d):
        """Update database with fetched data for a single day."""
        engine = create_engine(get_database_url())
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Ensure company exists
            company_exist_in_company_table = session.query(models.Company).filter(models.Company.company_ticker==ticker).first() is not None
            if not company_exist_in_company_table:
                new_company = models.Company(company_ticker = ticker)
                session.add(new_company)
                session.commit()

            # Ensure trade date exists
            date_exist_in_trade_date_table = session.query(models.TradeDate).filter(models.TradeDate.trade_date==date).first() is not None
            if not date_exist_in_trade_date_table:
                new_date = models.TradeDate(trade_date = date)
                session.add(new_date)
                session.commit()

            # Get IDs
            company_id = session.query(models.Company).filter(models.Company.company_ticker==ticker).first().company_id
            tradedate_id = session.query(models.TradeDate).filter(models.TradeDate.trade_date==date).first().trade_date_id

            # Ensure daily metrics exists
            company_date_pair_exist_in_table = session.query(models.DailyMetrics).filter(and_(models.DailyMetrics.company_id==company_id, models.DailyMetrics.trade_date_id==tradedate_id)).first() is not None
            if not company_date_pair_exist_in_table:
                new_company_date_pair = models.DailyMetrics(company_id = company_id, trade_date_id=tradedate_id)
                session.add(new_company_date_pair)
                session.commit()

            # Add fundamentals
            daily_metrics_id = session.query(models.DailyMetrics).filter(and_(models.DailyMetrics.company_id==company_id, models.DailyMetrics.trade_date_id==tradedate_id)).first().id
            fund_exits = session.query(models.Fundamentals).filter(models.Fundamentals.daily_metrics_id==daily_metrics_id).first() is not None
            if not fund_exits:
                new_fund = models.Fundamentals(
                    daily_metrics_id = daily_metrics_id,
                    open_price = d["open_price"],
                    high_price = d["high_price"],
                    close_price = d["close_price"],
                    low_price = d["low_price"],
                    volume = d["volume"],
                )
                session.add(new_fund)
                session.commit()
                return True
            else:
                # Data already exists, skip
                return False
        finally:
            session.close()

    def run(self, ag):
        fetch = YFinanceFetcher()
        ticker = ag.ticker

        # Parse start date
        if ag.start:
            start_date = datetime.strptime(ag.start, "%Y-%m-%d").date()
        else:
            # Get earliest available date for this ticker
            print(f"Fetching earliest available date for {ticker}...")
            earliest_date = fetch.get_earliest_date(ticker)
            if earliest_date is None:
                print(f"Error: Could not determine earliest date for {ticker}. Exiting.")
                return
            start_date = earliest_date
            print(f"Earliest available date: {start_date}")

        # Parse end date
        if ag.end:
            end_date = datetime.strptime(ag.end, "%Y-%m-%d").date()
        else:
            # Default to yesterday
            utc_dt = datetime.now(timezone.utc)
            end_date = (utc_dt - timedelta(days=1)).date()

        print(f"Starting backfill for {ticker}")
        print(f"Date range: {start_date} to {end_date}")
        print()

        # Fetch all historical data at once
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = (end_date + timedelta(days=1)).strftime("%Y-%m-%d")  # yfinance end date is exclusive

        print(f"Downloading historical data from yfinance...")
        historical_data = fetch.fetch_history(ticker, start_date_str, end_date_str)

        if historical_data is None:
            print(f"Error: Could not fetch historical data for {ticker}. Exiting.")
            return

        print(f"Downloaded {len(historical_data)} trading days of data")
        print()

        # Process each day's data
        successful = 0
        skipped = 0
        failed = 0

        for data in historical_data:
            trade_date = data["trade_date"]
            date_str = trade_date.strftime("%Y-%m-%d")

            try:
                # Update database
                inserted = self.update_database(ticker, trade_date, data)
                if inserted:
                    successful += 1
                    print(f"✓ {date_str}: Data inserted")
                else:
                    skipped += 1
                    print(f"○ {date_str}: Data already exists, skipped")
            except Exception as e:
                failed += 1
                print(f"✗ {date_str}: Failed to insert - {e}")

        print()
        print("=" * 50)
        print(f"Backfill completed for {ticker}")
        print(f"Total trading days received: {len(historical_data)}")
        print(f"Successfully inserted: {successful}")
        print(f"Skipped (already exists): {skipped}")
        print(f"Failed (database error): {failed}")
        print("=" * 50)
