import logging
import yfinance as yf
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class MarketData:
    """Class for fetching market-wide economic data"""
    
    def __init__(self, stock=None, date: Optional[datetime] = None):
        self.stock = stock
        self.date = date
    
    pass 
    # TODO: Add methods for fetching market data