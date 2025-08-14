"""Tickersync models - imports db models for data writing operations."""

# Import all models from db/models for use in tickersync operations
from taro.db.models import (
    Base,
    DailyMetrics,
    Fundamentals
)

# Re-export for convenience - tickersync primarily writes to these tables
__all__ = [
    'Base',
    'DailyMetrics',   # tickersync creates daily metrics records
    'Fundamentals',   # tickersync writes OHLC data here
]
