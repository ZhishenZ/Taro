"""Domain models for analysis (DDD) - Metric aggregates DailyMetrics and Fundamentals."""

from dataclasses import dataclass
from datetime import date

@dataclass
class FundamentalMetric:
    ticker: str
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

    @classmethod
    def from_orm(cls, daily_metrics, fundamentals):
        return cls(
            ticker=daily_metrics.ticker,
            trade_date=daily_metrics.trade_date,
            open=float(fundamentals.open_price),
            high=float(fundamentals.high_price),
            low=float(fundamentals.low_price),
            close=float(fundamentals.close_price),
            volume=int(fundamentals.volume)
        )

    def price_range(self) -> float:
        return self.high - self.low

    def is_bullish(self) -> bool:
        return self.close > self.open
