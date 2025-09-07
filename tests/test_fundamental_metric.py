"""Unit tests for FundamentalMetric domain model."""

import pytest
from datetime import date
from unittest.mock import Mock
from taro.analysis.domain.models import FundamentalMetric


class TestFundamentalMetric:
    """Test cases for FundamentalMetric domain model."""

    def test_fundamental_metric_creation(self):
        """Test creating a FundamentalMetric instance."""
        metric = FundamentalMetric(
            ticker="AAPL",
            trade_date=date(2023, 1, 15),
            open=150.0,
            high=155.0,
            low=148.0,
            close=153.0,
            volume=1000000
        )

        assert metric.ticker == "AAPL"
        assert metric.trade_date == date(2023, 1, 15)
        assert metric.open == 150.0
        assert metric.high == 155.0
        assert metric.low == 148.0
        assert metric.close == 153.0
        assert metric.volume == 1000000

    def test_price_range_calculation(self):
        """Test price range calculation."""
        metric = FundamentalMetric(
            ticker="AAPL",
            trade_date=date(2023, 1, 15),
            open=150.0,
            high=155.0,
            low=148.0,
            close=153.0,
            volume=1000000
        )

        assert metric.price_range() == 7.0  # 155.0 - 148.0

    def test_is_bullish_true(self):
        """Test is_bullish returns True when close > open."""
        metric = FundamentalMetric(
            ticker="AAPL",
            trade_date=date(2023, 1, 15),
            open=150.0,
            high=155.0,
            low=148.0,
            close=153.0,  # close > open
            volume=1000000
        )

        assert metric.is_bullish() is True

    def test_is_bullish_false(self):
        """Test is_bullish returns False when close <= open."""
        metric = FundamentalMetric(
            ticker="AAPL",
            trade_date=date(2023, 1, 15),
            open=150.0,
            high=155.0,
            low=148.0,
            close=147.0,  # close < open
            volume=1000000
        )

        assert metric.is_bullish() is False

    def test_from_orm_method(self):
        """Test creating FundamentalMetric from ORM objects."""
        # Mock ORM objects
        mock_daily_metrics = Mock()
        mock_daily_metrics.ticker = "TSLA"
        mock_daily_metrics.trade_date = date(2023, 2, 20)

        mock_fundamentals = Mock()
        mock_fundamentals.open_price = 200.50
        mock_fundamentals.high_price = 210.75
        mock_fundamentals.low_price = 195.25
        mock_fundamentals.close_price = 205.00
        mock_fundamentals.volume = 2500000

        metric = FundamentalMetric.from_orm(mock_daily_metrics, mock_fundamentals)

        assert metric.ticker == "TSLA"
        assert metric.trade_date == date(2023, 2, 20)
        assert metric.open == 200.50
        assert metric.high == 210.75
        assert metric.low == 195.25
        assert metric.close == 205.00
        assert metric.volume == 2500000

    def test_from_orm_type_conversion(self):
        """Test that from_orm properly converts types."""
        mock_daily_metrics = Mock()
        mock_daily_metrics.ticker = "GOOGL"
        mock_daily_metrics.trade_date = date(2023, 3, 10)

        mock_fundamentals = Mock()
        # Use string/decimal types that need conversion
        mock_fundamentals.open_price = "100.25"
        mock_fundamentals.high_price = "105.50"
        mock_fundamentals.low_price = "98.75"
        mock_fundamentals.close_price = "103.00"
        mock_fundamentals.volume = "1500000"

        metric = FundamentalMetric.from_orm(mock_daily_metrics, mock_fundamentals)

        # Verify types are converted properly
        assert isinstance(metric.open, float)
        assert isinstance(metric.high, float)
        assert isinstance(metric.low, float)
        assert isinstance(metric.close, float)
        assert isinstance(metric.volume, int)

        assert metric.open == 100.25
        assert metric.high == 105.50
        assert metric.low == 98.75
        assert metric.close == 103.00
        assert metric.volume == 1500000

    def test_edge_case_equal_open_close(self):
        """Test is_bullish when open equals close."""
        metric = FundamentalMetric(
            ticker="MSFT",
            trade_date=date(2023, 4, 5),
            open=250.0,
            high=255.0,
            low=248.0,
            close=250.0,  # close == open
            volume=800000
        )

        assert metric.is_bullish() is False  # Not bullish when equal

    def test_zero_price_range(self):
        """Test price range when high equals low."""
        metric = FundamentalMetric(
            ticker="AMZN",
            trade_date=date(2023, 5, 12),
            open=100.0,
            high=100.0,  # same as low
            low=100.0,
            close=100.0,
            volume=500000
        )

        assert metric.price_range() == 0.0
