import logging
import yfinance as yf
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class OptionsData:
    """Class for fetching options data and calculating options-based metrics"""
    
    def __init__(self, stock, date: Optional[datetime] = None):
        self.stock = stock
        self.date = date
    pass 
    # TODO: Add methods for fetching options data and calculating metrics