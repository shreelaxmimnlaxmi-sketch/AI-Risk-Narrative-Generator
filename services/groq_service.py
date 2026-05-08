from typing import Optional

from groq import Client


class GroqService:
    def __init__(self, api_key: str, model: str = 'llama-3.3-70b-versatile') -> None:
        self.api_key = api_key
        self.model = model
        self.client = Client(api_key=self.api_key)

    def generate_text(self, prompt: str, timeout: int = 18) -> Optional[str]:
        if not self.api_key:
            raise ValueError('Groq API key is not configured.')

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.2,
            top_p=0.9,
            max_completion_tokens=512,
            stop=['```'],
            timeout=timeout,
        )

        if hasattr(response, 'choices') and response.choices:
            first_choice = response.choices[0]
            if hasattr(first_choice, 'message') and getattr(first_choice.message, 'content', None) is not None:
                return first_choice.message.content
            if hasattr(first_choice, 'text'):
                return first_choice.text
        if hasattr(response, 'output_text'):
            return response.output_text
        if isinstance(response, str):
            return response
        if hasattr(response, 'text'):
            return response.text
        return str(response)
