from unittest.mock import AsyncMock

from app import app


def test_recommend_endpoint_success():
    client = app.test_client()
    payload = {
        'risk_type': 'Cybersecurity',
        'severity': 'High',
        'details': 'Potential phishing attack detected',
    }

    mocked_response = {
        'recommendations': [
            {'action_type': 'Preventive', 'description': 'Implement email filtering.', 'priority': 'High'},
            {'action_type': 'Detective', 'description': 'Monitor phishing patterns.', 'priority': 'Medium'},
            {'action_type': 'Corrective', 'description': 'Train staff on phishing awareness.', 'priority': 'High'},
        ]
    }

    app.config['AI_SERVICE'] = AsyncMock()
    app.config['AI_SERVICE'].generate.return_value = mocked_response
    response = client.post('/recommend', json=payload)

    assert response.status_code == 200
    result = response.get_json()
    assert result['success'] is True
    assert len(result['recommendations']) == 3
