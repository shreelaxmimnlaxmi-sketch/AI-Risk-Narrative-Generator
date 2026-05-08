import asyncio
import asyncio
from datetime import datetime
from flask import Blueprint, current_app, jsonify, request

from utils.validator import sanitize_text, validate_payload

describe_bp = Blueprint('describe_routes', __name__)


@describe_bp.route('/describe', methods=['GET', 'POST'])
def describe_risk():
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'endpoint': '/describe',
            'method': 'POST',
            'description': 'Generate a professional risk narrative from risk_type, severity, and details.',
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
    result = asyncio.run(ai_service.generate('describe_prompt.txt', sanitized_input, 'describe'))

    if result.get('is_fallback'):
        return jsonify({'success': False, 'is_fallback': True, 'message': result.get('message')}), 503

    description = result.get('risk_description')
    if not description:
        return jsonify({'success': False, 'message': 'Unable to generate risk description'}), 502

    return jsonify({
        'success': True,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'risk_description': description.strip(),
    }), 200
