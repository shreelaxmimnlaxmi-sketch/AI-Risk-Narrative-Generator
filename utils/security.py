import re
import time
from flask import Response, Request
from typing import Dict, Tuple


class RateLimiter:
    def __init__(self, request_limit: int = 20, window_seconds: int = 60) -> None:
        self.request_limit = request_limit
        self.window_seconds = window_seconds
        self.cache: Dict[str, Dict[str, float]] = {}

    def allow_request(self, client_ip: str) -> Tuple[bool, int]:
        entry = self.cache.get(client_ip, {'count': 0, 'reset_at': time.time() + self.window_seconds})
        now = time.time()
        if now > entry['reset_at']:
            entry = {'count': 0, 'reset_at': now + self.window_seconds}
        entry['count'] += 1
        self.cache[client_ip] = entry
        remaining = max(0, self.request_limit - entry['count'])
        return (entry['count'] <= self.request_limit, remaining)


def apply_security_headers(response: Response) -> Response:
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none';"
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def is_json_content(request: Request) -> bool:
    content_type = request.headers.get('Content-Type', '')
    return content_type.startswith('application/json')
