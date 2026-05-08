import json
from unittest.mock import AsyncMock, patch

from app import app


def test_describe_endpoint_success():
    client = app.test_client()
    payload = {
        'risk_type': 'Cybersecurity',
        'severity': 'High',
        'details': 'Potential phishing attack detected',
    }

    mocked_response = {'risk_description': 'A high-severity cybersecurity risk from a potential phishing attack is identified.'}
    with patch('app.current_app.config', app.config):
        app.config['AI_SERVICE'] = AsyncMock()
        app.config['AI_SERVICE'].generate.return_value = mocked_response
        response = client.post('/describe', json=payload)

    assert response.status_code == 200
    result = response.get_json()
    assert result['success'] is True
    assert 'risk_description' in result
