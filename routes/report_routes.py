import asyncio
from flask import Blueprint, current_app, jsonify, request

from utils.validator import sanitize_text, validate_payload

report_bp = Blueprint('report_routes', __name__)


@report_bp.route('/generate-report', methods=['GET', 'POST'])
@report_bp.route('/report', methods=['GET', 'POST'])
def generate_report():
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'endpoints': ['/generate-report', '/report'],
            'method': 'POST',
            'description': 'Generate a structured executive report from the provided risk context.',
            'example_payload': {
                'risk_type': 'Cybersecurity',
                'severity': 'High',
                'details': 'Potential phishing attack detected',
            },
        }), 200

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400

    required_fields = {'risk_type': 3, 'severity': 2, 'details': 10}
    errors = validate_payload(payload, required_fields)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    sanitized_input = {field: sanitize_text(payload[field]) for field in required_fields}
    ai_service = current_app.config['AI_SERVICE']
    result = asyncio.run(ai_service.generate('report_prompt.txt', sanitized_input, 'report'))

    if result.get('is_fallback'):
        return jsonify({'success': False, 'is_fallback': True, 'message': result.get('message')}), 503

    if not isinstance(result, dict):
        return jsonify({'success': False, 'message': 'Unable to generate report content'}), 502

    return jsonify({
        'title': result.get('title', ''),
        'summary': result.get('summary', ''),
        'overview': result.get('overview', ''),
        'key_items': result.get('key_items', []),
        'recommendations': result.get('recommendations', []),
    }), 200
