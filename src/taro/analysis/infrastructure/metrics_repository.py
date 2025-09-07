from taro.db.models import DailyMetrics, Fundamentals
from taro.analysis.domain.models import FundamentalMetric

class MetricsRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_all_metrics(self):
        session = self.session_factory()
        try:
            results = (
                session.query(DailyMetrics, Fundamentals)
                .join(Fundamentals, Fundamentals.daily_metrics_id == DailyMetrics.id)
                .all()
            )
            return [FundamentalMetric.from_orm(dm, f) for dm, f in results]
        finally:
            session.close()

    def get_metrics_for_ticker(self, ticker):
        session = self.session_factory()
        try:
            results = (
                session.query(DailyMetrics, Fundamentals)
                .join(Fundamentals, Fundamentals.daily_metrics_id == DailyMetrics.id)
                .filter(DailyMetrics.ticker == ticker)
                .all()
            )
            return [FundamentalMetric.from_orm(dm, f) for dm, f in results]
        finally:
            session.close()
