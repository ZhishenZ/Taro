
from taro.analysis.infrastructure.metrics_repository import MetricsRepository

class MetricsService:
    def __init__(self, session_factory):
        self.repository = MetricsRepository(session_factory)

    def get_overall_metrics(self):
        metrics = self.repository.get_all_metrics()
        return {
            'count': len(metrics),
            'metrics': [m.__dict__ for m in metrics]
        }

    def get_metrics_for_ticker(self, ticker):
        metrics = self.repository.get_metrics_for_ticker(ticker)
        latest_date = max((m.trade_date for m in metrics), default=None)
        return {
            'ticker': ticker,
            'count': len(metrics),
            'latest_date': str(latest_date) if latest_date else None,
            'metrics': [m.__dict__ for m in metrics]
        }
