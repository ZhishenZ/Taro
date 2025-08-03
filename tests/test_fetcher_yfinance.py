from datetime import datetime, timedelta
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from taro.fetcher.fetcher_yfinance import YFinanceFetcher


class TestYFinanceFetcher:
    """Tests for YFinanceFetcher class - testing real API calls"""

    def setup_method(self):
        """Setup before each test method"""
        self.fetcher = YFinanceFetcher()

    def test_sunday_should_return_none(self):
        """Test that Sunday (2025-03-09) should return None"""
        test_date = "2025-03-09"  # Sunday
        result = self.fetcher.fetch_by_date('GOOGL', test_date)
        # Should return None for Sunday
        assert (
            result is None
        ), f"Expected None for Sunday {test_date}, but got: {result}"

    def test_monday_should_return_data(self):
        """Test that Monday (2025-03-10) should return data"""
        test_date = "2025-03-10"  # Monday
        result = self.fetcher.fetch_by_date('GOOGL', test_date)
        # Should return data for Monday
        assert result is not None, f"Expected data for Monday {test_date}, but got None"

        # Verify data structure
        assert 'trade_date' in result, "Missing trade_date field"
        assert 'ticker' in result, "Missing ticker field"
        assert 'open_price' in result, "Missing open_price field"
        assert 'high_price' in result, "Missing high_price field"
        assert 'low_price' in result, "Missing low_price field"
        assert 'close_price' in result, "Missing close_price field"
        assert 'volume' in result, "Missing volume field"

        # Verify data values
        assert (
            result['ticker'] == 'GOOGL'
        ), f"Expected ticker GOOGL, got {result['ticker']}"
        assert (
            result['open_price'] > 0
        ), f"Expected positive open_price, got {result['open_price']}"
        assert (
            result['high_price'] > 0
        ), f"Expected positive high_price, got {result['high_price']}"
        assert (
            result['low_price'] > 0
        ), f"Expected positive low_price, got {result['low_price']}"
        assert (
            result['close_price'] > 0
        ), f"Expected positive close_price, got {result['close_price']}"
        assert result['volume'] > 0, f"Expected positive volume, got {result['volume']}"

    def test_future_date_should_return_none(self):
        """Test that future date should return None"""
        # Use a date 30 days in the future
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        result = self.fetcher.fetch_by_date('GOOGL', future_date)
        # Should return None for future date
        assert (
            result is None
        ), f"Expected None for future date {future_date}, but got: {result}"
