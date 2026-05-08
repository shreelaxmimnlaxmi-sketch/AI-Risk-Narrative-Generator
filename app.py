import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

from routes.describe_routes import describe_bp
from routes.recommend_routes import recommend_bp
from routes.report_routes import report_bp
from routes.health_routes import health_bp
from services.groq_service import GroqService
from services.cache_service import CacheService
from services.async_service import AsyncService
from services.ai_service_client import AiServiceClient
from utils.logger import setup_logging
from utils.security import apply_security_headers, RateLimiter, is_json_content

load_dotenv()

START_TIME = time.time()
METRICS = {
    'request_count': 0,
    'total_time': 0.0,
}


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        GROQ_API_KEY=os.getenv('GROQ_API_KEY', ''),
        REDIS_HOST=os.getenv('REDIS_HOST', 'localhost'),
        REDIS_PORT=int(os.getenv('REDIS_PORT', 6379)),
        FLASK_ENV=os.getenv('FLASK_ENV', 'production'),
        MODEL_NAME='llama-3.3-70b-versatile',
        RATE_LIMIT_REQUESTS=20,
        RATE_LIMIT_WINDOW=60,
    )

    setup_logging(app)
    CORS(app, resources={r'/*': {'origins': '*'}})

    cache_service = CacheService(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
    )
    groq_service = GroqService(
        api_key=app.config['GROQ_API_KEY'],
        model=app.config['MODEL_NAME'],
    )
    async_service = AsyncService()
    ai_service = AiServiceClient(
        groq_service=groq_service,
        cache_service=cache_service,
        async_service=async_service,
    )

    app.config['CACHE_SERVICE'] = cache_service
    app.config['AI_SERVICE'] = ai_service
    app.config['RATE_LIMITER'] = RateLimiter(
        request_limit=app.config['RATE_LIMIT_REQUESTS'],
        window_seconds=app.config['RATE_LIMIT_WINDOW'],
    )
    app.config['START_TIME'] = START_TIME
    app.config['METRICS'] = METRICS

    app.register_blueprint(describe_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(health_bp)

    @app.before_request
    def before_request() -> None:
        if request.method in ('POST', 'PUT', 'PATCH') and not is_json_content(request):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400

        client_ip = request.remote_addr or 'unknown'
        limiter = app.config['RATE_LIMITER']
        allowed, remaining = limiter.allow_request(client_ip)
        if not allowed:
            return jsonify({'success': False, 'message': 'Rate limit exceeded'}), 429
        request.environ['rate_limit_remaining'] = remaining

    @app.route('/', methods=['GET'])
    def index():
        return render_template(
            'index.html',
            api_configured=bool(app.config['GROQ_API_KEY']),
            model_name=app.config.get('MODEL_NAME', 'llama-3.3-70b-versatile'),
        )

    @app.route('/api', methods=['GET'])
    def api_docs():
        return jsonify({
            'service': 'AI Risk Narrative Generator',
            'status': 'running',
            'model': app.config.get('MODEL_NAME', 'llama-3.3-70b-versatile'),
            'endpoints': {
                'POST /describe': 'Generate a professional risk narrative',
                'POST /recommend': 'Generate three risk recommendations',
                'POST /generate-report': 'Generate a structured executive report',
                'GET /report': 'Endpoint docs and alias for /generate-report',
                'GET /health': 'Service health and cache status',
            },
            'documentation': 'Send JSON payload with risk_type, severity, and details to POST endpoints.',
        }), 200

    @app.after_request
    def after_request(response):
        response = apply_security_headers(response)
        return response

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False, 'message': 'Bad request', 'details': str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'message': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception('Internal server error')
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

    @app.after_request
    def measure_latency(response):
        elapsed = time.time() - float(request.environ.get('werkzeug.request_start_time', time.time()))
        METRICS['request_count'] += 1
        METRICS['total_time'] += elapsed
        return response

    @app.before_request
    def track_request_start() -> None:
        request.environ['werkzeug.request_start_time'] = time.time()

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
