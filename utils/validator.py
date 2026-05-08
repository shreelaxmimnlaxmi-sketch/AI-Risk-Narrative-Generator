import json
import re
from typing import Any, Dict

MAX_FIELD_LENGTH = 512


def sanitize_text(value: str) -> str:
    if not isinstance(value, str):
        return ''
    value = value.strip()
    value = re.sub(r'[\x00-\x1F\x7F]+', ' ', value)
    value = re.sub(r'<[^>]+>', '', value)
    return value[:MAX_FIELD_LENGTH]


def detect_prompt_injection(value: str) -> bool:
    injection_patterns = [
        r'ignore previous',
        r'disregard instructions',
        r'system prompt',
        r'assistant should',
        r'openai',
        r'chatgpt',
        r'you are a',
        r'<script>',
    ]
    normalized = value.lower()
    return any(re.search(pattern, normalized) for pattern in injection_patterns)


def validate_payload(payload: Dict[str, Any], required_fields: Dict[str, int]) -> Dict[str, str]:
    errors = {}
    for field, min_len in required_fields.items():
        raw_value = payload.get(field)
        if raw_value is None or not isinstance(raw_value, str) or not raw_value.strip():
            errors[field] = 'Field is required and must be a non-empty string.'
            continue
        sanitized = sanitize_text(raw_value)
        if len(sanitized) < min_len:
            errors[field] = f'Field must contain at least {min_len} characters.'
            continue
        if detect_prompt_injection(sanitized):
            errors[field] = 'Potential prompt injection detected.'
    return errors


def parse_model_output(content: str) -> Any:
    try:
        cleaned = content.strip()
        if cleaned.startswith('```') and cleaned.endswith('```'):
            cleaned = '\n'.join(cleaned.splitlines()[1:-1])
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None
