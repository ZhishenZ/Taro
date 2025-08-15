import yfinance as yf
from datetime import datetime, timedelta, date as date_type
from typing import List, Dict
import pandas as pd


class YFinanceFetcher:
    def get_earliest_date(self, ticker: str) -> date_type | None:
        """
        Get the earliest available trading date for a ticker.
        :param ticker: Stock symbol, e.g. 'GOOGL'
        :return: date object or None if error
        """
        try:
            # Fetch maximum history available
            stock = yf.Ticker(ticker)
            df = stock.history(period="max", auto_adjust=True)

            if df.empty:
                print(f"No historical data available for {ticker}")
                return None

            earliest_date = df.index[0].date()
            return earliest_date
        except Exception as e:
            print(f"Exception occurred while fetching earliest date for {ticker}: {e}")
            return None

    def fetch_history(self, ticker: str, start_date: str, end_date: str) -> List[Dict] | None:
        """
        Fetch historical market data for a stock over a date range.
        :param ticker: Stock symbol, e.g. 'GOOGL'
        :param start_date: Start date string, e.g. '2020-01-01'
        :param end_date: End date string, e.g. '2024-12-31'
        :return: List of dictionaries containing daily data, or None if error
        """
        try:
            # Download data for the entire range
            # auto_adjust=True returns adjusted (total return) prices, accounting for splits/dividends
            df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)

            if df.empty:
                print(f"No trading data found for {ticker} between {start_date} and {end_date}")
                return None

            # Flatten the MultiIndex columns if present (happens when downloading single ticker)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            results = []
            for index, row in df.iterrows():
                try:
                    # Extract values directly
                    open_price = row["Open"]
                    high_price = row["High"]
                    low_price = row["Low"]
                    close_price = row["Close"]
                    volume = row["Volume"]

                    # Check if any value is NaN
                    if pd.isna(open_price) or pd.isna(high_price) or pd.isna(low_price) or pd.isna(close_price) or pd.isna(volume):
                        continue

                    results.append({
                        "trade_date": index.date(),
                        "ticker": ticker,
                        "open_price": float(open_price),
                        "high_price": float(high_price),
                        "low_price": float(low_price),
                        "close_price": float(close_price),
                        "volume": int(volume),
                    })
                except (KeyError, ValueError, TypeError):
                    # Skip rows with missing or invalid data
                    continue

            return results if results else None

        except Exception as e:
            print(f"Exception occurred while fetching history for {ticker}: {e}")
            return None

    def fetch_by_date(self, ticker: str, date: str) -> dict | None:
        """
        Fetch the market data for a specific stock on a given day.
        :param ticker: Stock symbol, e.g. 'GOOGL'
        :param date: Date string, e.g. '2023-01-05'
        :return: dict or None
        """
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            next_day = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

            # Use fetch_history to get data for this single date
            results = self.fetch_history(ticker, date, next_day)

            if results is None or len(results) == 0:
                print(f"No trading data for {ticker} on {date} (possibly a holiday or invalid symbol)")
                return None

            # Find the data for the requested date
            for data in results:
                if data["trade_date"] == date_obj.date():
                    return data

            # If we didn't find the exact date, return None
            print(f"No trading data for {ticker} on {date} (possibly a holiday or invalid symbol)")
            return None

        except Exception as e:
            print(f"Exception occurred while fetching data for {ticker} on {date}: {e}")
            return None
