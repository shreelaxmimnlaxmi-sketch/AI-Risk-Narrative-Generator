from unittest.mock import AsyncMock

from app import app


def test_generate_report_endpoint_success():
    client = app.test_client()
    payload = {
        'risk_type': 'Cybersecurity',
        'severity': 'High',
        'details': 'Potential phishing attack detected',
    }

    mocked_response = {
        'title': 'Phishing Risk Advisory',
        'summary': 'A high-severity phishing risk threatens employees and data security.',
        'overview': 'A potential phishing attack was identified, which could expose user credentials and internal systems.',
        'key_items': ['Phishing source identified', 'High severity', 'Recommended training and controls'],
        'recommendations': [
            {'action_type': 'Preventive', 'description': 'Enhance email security controls.', 'priority': 'High'},
        ],
    }

    app.config['AI_SERVICE'] = AsyncMock()
    app.config['AI_SERVICE'].generate.return_value = mocked_response
    response = client.post('/generate-report', json=payload)

    assert response.status_code == 200
    result = response.get_json()
    assert 'title' in result
    assert 'summary' in result
    assert isinstance(result['recommendations'], list)
