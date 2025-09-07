"""Analysis application module - sets up Flask app and integrates components."""

from flask import Flask
from .infrastructure.db import get_database_url, Session
from .application.metrics_service import MetricsService
from .presentation.analysis_blueprint import create_analysis_blueprint

def create_app():
    app = Flask(__name__)
    app.config['DATABASE_URL'] = get_database_url()

    # Direct dependency injection
    metrics_service = MetricsService(Session)
    analysis_bp = create_analysis_blueprint(metrics_service)
    app.register_blueprint(analysis_bp)
    return app

def main():
    print('start analysis service!')
    app = create_app()
    app.run(debug=True, port=5001)

if __name__ == '__main__':
    main()
