
from flask import Blueprint, jsonify, current_app

def create_analysis_blueprint(metrics_service):
    analysis_bp = Blueprint('analysis', __name__)

    @analysis_bp.route('/health')
    def health_check():
        db_url = current_app.config.get('DATABASE_URL', 'not set')
        return jsonify({'status': 'healthy', 'service': 'analysis', 'database': db_url})

    @analysis_bp.route('/tables')
    def list_tables():
        from taro.db.models import Base
        tables = list(Base.metadata.tables.keys())
        return jsonify({'tables': tables, 'service': 'analysis'})


    @analysis_bp.route('/metrics')
    def get_metrics():
        result = metrics_service.get_overall_metrics()
        # result['metrics'] contains FundamentalMetric objects as dicts
        return jsonify(result)

    @analysis_bp.route('/metrics/<ticker>')
    def get_metrics_for_ticker(ticker):
        result = metrics_service.get_metrics_for_ticker(ticker)
        # result['metrics'] contains FundamentalMetric objects as dicts
        return jsonify(result)

    return analysis_bp
