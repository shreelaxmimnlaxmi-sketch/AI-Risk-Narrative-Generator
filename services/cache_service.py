import hashlib
import json
from typing import Any, Dict, Optional

import redis


class CacheService:
    def __init__(self, host: str = 'localhost', port: int = 6379, ttl: int = 900) -> None:
        self.ttl = ttl
        self.client = redis.Redis(
            host=host,
            port=port,
            socket_timeout=5,
            decode_responses=True,
        )

    def generate_cache_key(self, namespace: str, payload: Dict[str, Any]) -> str:
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()
        return f'{namespace}:{fingerprint}'

    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
        except redis.RedisError:
            return None
        return None

    def set(self, key: str, value: Any) -> None:
        try:
            self.client.set(key, json.dumps(value), ex=self.ttl)
        except redis.RedisError:
            pass

    def health(self) -> str:
        try:
            if self.client.ping():
                return 'connected'
        except redis.RedisError:
            pass
        return 'unavailable'
