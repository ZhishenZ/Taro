import yfinance as yf
from datetime import datetime, timedelta


class YFinanceFetcher:
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
            # progress=False disables the download progress print
            # auto_adjust=True returns adjusted (total return) prices, accounting for splits/dividends
            df = yf.download(
                ticker, start=date, end=next_day, progress=False, auto_adjust=True
            )

            if df.empty or date_obj.date() not in df.index.date:
                print(
                    f"No trading data for {ticker} on {date} (possibly a holiday or invalid symbol)"
                )
                return None
            row = df.loc[df.index.date == date_obj.date()].iloc[0]
            trade_date = date_obj.date()
            # Check for missing key fields
            for col in ["Open", "High", "Low", "Close", "Volume"]:
                if col not in row or row[col] is None:
                    print(f"Missing field {col} for {ticker} on {date}")
                    return None
            return {
                "trade_date": trade_date,
                "ticker": ticker,
                "open_price": float(row["Open"].iloc[0]),
                "high_price": float(row["High"].iloc[0]),
                "low_price": float(row["Low"].iloc[0]),
                "close_price": float(row["Close"].iloc[0]),
                "volume": float(row["Volume"].iloc[0]),
            }
        except Exception as e:
            print(f"Exception occurred while fetching data for {ticker} on {date}: {e}")
            return None
