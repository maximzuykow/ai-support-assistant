import os
import time
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
        return response.json()['choices'][0]['message']['content'].strip()


class MockLLMProvider(BaseLLMProvider):
    def generate(self, prompt: str) -> str:
        time.sleep(5)

        return (
            'Thank you for contacting our support team. '
            'We have received your request and will review it shortly.'
        )


def get_llm_provider() -> BaseLLMProvider:
    provider = os.getenv('LLM_PROVIDER', 'mock').lower()

    if provider == 'openai':
        return OpenAIProvider()

    if provider == 'mock':
        return MockLLMProvider()

    raise ValueError(f'Unsupported LLM provider: {provider}')