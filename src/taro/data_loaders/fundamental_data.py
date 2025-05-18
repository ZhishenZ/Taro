import logging
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

class FundamentalData:
    """Class for fetching and storing basic trading data for a company"""
    
    def __init__(self, stock, date: datetime):
        """
        Initialize with a stock object and date
        
        Args:
            stock: yfinance Ticker object
            date: target date (datetime object)
        """
        self.stock = stock
        self.ticker = stock.ticker
        
        # Trading data attributes
        self.open: Optional[float] = None
        self.close: Optional[float] = None
        self.high: Optional[float] = None
        self.low: Optional[float] = None
        self.volume: Optional[int] = None
        
        # Fetch data directly
        self.fetch_trading_data(date)
    
    def fetch_trading_data(self, date: datetime) -> bool:
        """
        Fetch trading data for a specific date
        
        Args:
            date: target date
            
        Returns:
            bool: whether data was successfully retrieved
        """
        try:
            # Directly fetch data for the specified date
            hist = self.stock.history(start=date, end=date + timedelta(days=1))
            
            if hist.empty:
                logger.info(f"No trading data available for {self.ticker} on {date}")
                return False
            
            # Store data to object attributes
            self.open = float(hist['Open'].iloc[0])
            self.close = float(hist['Close'].iloc[0])
            self.high = float(hist['High'].iloc[0])
            self.low = float(hist['Low'].iloc[0])
            self.volume = int(hist['Volume'].iloc[0])
            return True
            
        except Exception as e:
            logger.warning(f"Error fetching trading data for {self.ticker}: {e}")
            return False
    
    # Ask my colleague if she needs this function
    def to_dict(self):
        """
        Convert data to dictionary format
        
        Returns:
            Dictionary containing trading data
        """
        return {
            'open': self.open,
            'close': self.close,
            'high': self.high,
            'low': self.low,
            'volume': self.volume
        }
        
    def __str__(self):
        """String representation for printing the object"""
        return (f"FundamentalData({self.ticker}): "
                f"Open=${self.open:.2f if self.open else 'N/A'}, "
                f"Close=${self.close:.2f if self.close else 'N/A'}, "
                f"High=${self.high:.2f if self.high else 'N/A'}, "
                f"Low=${self.low:.2f if self.low else 'N/A'}, "
                f"Volume={self.volume if self.volume else 'N/A'}") 