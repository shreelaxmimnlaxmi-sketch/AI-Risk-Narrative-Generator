import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional

from services.async_service import AsyncService
from services.cache_service import CacheService
from services.groq_service import GroqService
from utils.validator import parse_model_output

PROMPT_DIRECTORY = Path(__file__).resolve().parents[1] / 'prompts'


class AiServiceClient:
    def __init__(
        self,
        groq_service: GroqService,
        cache_service: CacheService,
        async_service: AsyncService,
    ) -> None:
        self.groq_service = groq_service
        self.cache_service = cache_service
        self.async_service = async_service
        self.prompt_cache: Dict[str, str] = {}

    def load_prompt(self, prompt_name: str) -> str:
        if prompt_name in self.prompt_cache:
            return self.prompt_cache[prompt_name]
        prompt_path = PROMPT_DIRECTORY / prompt_name
        if not prompt_path.exists():
            raise FileNotFoundError(f'Prompt file not found: {prompt_name}')
        content = prompt_path.read_text(encoding='utf-8')
        self.prompt_cache[prompt_name] = content
        return content

    def build_prompt(self, prompt_name: str, payload: Dict[str, Any]) -> str:
        prompt_template = self.load_prompt(prompt_name)
        prompt_text = prompt_template
        for key, value in payload.items():
            prompt_text = prompt_text.replace(f'{{{key}}}', str(value))
        return prompt_text

    async def generate(
        self,
        prompt_name: str,
        payload: Dict[str, Any],
        cache_namespace: str,
        timeout: int = 18,
    ) -> Dict[str, Any]:
        cache_key = self.cache_service.generate_cache_key(cache_namespace, payload)
        cached = self.cache_service.get(cache_key)
        if isinstance(cached, dict):
            return cached

        prompt_text = self.build_prompt(prompt_name, payload)
        attempt = 0
        last_error: Optional[Exception] = None
        while attempt < 2:
            try:
                raw_output = await asyncio.wait_for(
                    self.async_service.run_in_thread(self.groq_service.generate_text, prompt_text, timeout),
                    timeout=timeout + 2,
                )
                if not raw_output:
                    raise ValueError('Empty AI response from Groq service.')
                parsed = parse_model_output(raw_output)
                if not isinstance(parsed, dict):
                    raise ValueError('AI response did not return structured JSON.')
                self.cache_service.set(cache_key, parsed)
                return parsed
            except (asyncio.TimeoutError, ValueError, Exception) as exc:
                last_error = exc
                attempt += 1
                await asyncio.sleep(0.5)

        return {'is_fallback': True, 'message': 'AI service unavailable', 'error': str(last_error)}
