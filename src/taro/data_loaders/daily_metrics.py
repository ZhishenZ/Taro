import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from .fundamental_data import FundamentalData
from .technical_indicators import TechnicalIndicators
from .options_data import OptionsData
from .market_data import MarketData

logger = logging.getLogger(__name__)

class DailyMetrics:
    """Get daily trading data for stocks for a specific date"""
    
    def __init__(self, ticker: str, date: str | datetime):
        """
        Initialize daily metrics fetcher.
        
        Args:
            ticker: Stock ticker symbol (e.g., "GOOGL").
            date: Specific date to fetch data for (datetime object or string 'YYYY-MM-DD').
        
        Raises:
            ValueError: If the ticker is invalid or the date is invalid.
        """
        self.stock = yf.Ticker(ticker)

        # ticker validation check
        try:
            info = self.stock.info
            if 'symbol' not in info:
                raise ValueError(f"Invalid ticker: {ticker}")
        except Exception as e:
            raise ValueError(f"Invalid ticker: {ticker}")
        
        self.date = self._parse_date(date)
        
        # Initialize other data loaders
        self.fundamental = FundamentalData(self.stock, self.date)
        self.technical = TechnicalIndicators(self.stock, self.date)
        self.options = OptionsData(self.stock, self.date)
        self.market = MarketData(self.stock, self.date) # Market data accepts stock but doesn't strictly need it
        
    def _parse_date(self, date):
        if date is None:
            raise ValueError("Date argument is mandatory and cannot be None.")

        if isinstance(date, str):
            try:
                return datetime.strptime(date, '%Y-%m-%d')
            except ValueError as e:
                logger.error(f"Invalid date format for date: {date}. Please use YYYY-MM-DD.")
                raise ValueError(f"Invalid date format for date: {date}. Please use YYYY-MM-DD.") from e
        elif isinstance(date, datetime):
            return date
        else:
            raise ValueError("Date must be a string (YYYY-MM-DD) or a datetime object.")