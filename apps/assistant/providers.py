import os
from abc import ABC, abstractmethod

import httpx


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.base_url = 'https://api.openai.com/v1/chat/completions'

        if not self.api_key:
            raise ValueError('OPENAI_API_KEY is not configured')

    def generate(self, prompt: str) -> str:
        response = httpx.post(
            self.base_url,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt,
                    },
                ],
            },
            timeout=20.0,
        )

        response.raise_for_status()
        data = response.json()

        return data['choices'][0]['message']['content'].strip()