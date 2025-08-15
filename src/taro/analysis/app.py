"""Analysis application module."""

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from ..db.models import Base, DailyMetrics, Fundamentals
from ..utils import get_database_url
import os


def create_app():
    """Create and configure the analysis Flask app."""
    app = Flask(__name__)

    # PostgreSQL database configuration using shared models
    database_url = get_database_url()

    app.config['DATABASE_URL'] = database_url

    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'analysis', 'database': database_url}

    @app.route('/tables')
    def list_tables():
        """List all available tables in shared schema."""
        tables = list(Base.metadata.tables.keys())
        return {'tables': tables, 'service': 'analysis'}

    @app.route('/metrics')
    def get_metrics():
        """Get overall analysis metrics from shared tables."""
        session = Session()
        try:
            daily_metrics_count = session.query(func.count(DailyMetrics.id)).scalar()
            fundamentals_count = session.query(func.count(Fundamentals.id)).scalar()

            return {
                'total_daily_metrics': daily_metrics_count,
                'total_fundamentals': fundamentals_count
            }
        finally:
            session.close()

    @app.route('/metrics/<ticker>')
    def get_metrics_for_ticker(ticker):
        """Get metrics for a specific ticker from shared tables."""
        session = Session()
        try:
            data_count = session.query(func.count(DailyMetrics.id)).filter(
                DailyMetrics.ticker == ticker
            ).scalar()

            latest_date = session.query(DailyMetrics.trade_date).filter(
                DailyMetrics.ticker == ticker
            ).order_by(DailyMetrics.trade_date.desc()).first()

            return {
                'ticker': ticker,
                'data_points': data_count,
                'latest_date': str(latest_date[0]) if latest_date else None
            }
        finally:
            session.close()

    return app


if __name__ == '__main__':
    print('start analysis service!')
    # app = create_app()
    # app.run(debug=True, port=5001)
