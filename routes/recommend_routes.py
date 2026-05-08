import asyncio
from flask import Blueprint, current_app, jsonify, request

from utils.validator import sanitize_text, validate_payload

recommend_bp = Blueprint('recommend_routes', __name__)


@recommend_bp.route('/recommend', methods=['GET', 'POST'])
def recommend_actions():
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'endpoint': '/recommend',
            'method': 'POST',
            'description': 'Generate three professional AI recommendations for the provided risk context.',
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
    result = asyncio.run(ai_service.generate('recommend_prompt.txt', sanitized_input, 'recommend'))

    if result.get('is_fallback'):
        return jsonify({'success': False, 'is_fallback': True, 'message': result.get('message')}), 503

    recommendations = result.get('recommendations')
    if not isinstance(recommendations, list):
        return jsonify({'success': False, 'message': 'Unable to generate recommendations'}), 502

    return jsonify({'success': True, 'recommendations': recommendations}), 200
