import time
from flask import Blueprint, current_app, jsonify

health_bp = Blueprint('health_routes', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    app = current_app
    start_time = app.config.get('START_TIME', time.time())
    uptime_seconds = int(time.time() - start_time)
    average_response = '0.0s'
    metrics = app.config.get('METRICS', {})
    if metrics.get('request_count', 0) > 0:
        average_response = f"{metrics['total_time'] / metrics['request_count']:.2f}s"

    cache_status = app.config['CACHE_SERVICE'].health()
    return jsonify({
        'status': 'healthy',
        'model': app.config.get('MODEL_NAME', 'llama-3.3-70b-versatile'),
        'uptime': f'{uptime_seconds}s',
        'average_response_time': average_response,
        'cache': cache_status,
    }), 200
