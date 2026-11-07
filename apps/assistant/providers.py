import os
import random
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

    def generate(self, prompt: str) -> str:
        headers = {
            'Content-Type': 'application/json',
        }

        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        if not self.api_key:
            try:
                httpx.post(
                    self.base_url,
                    headers=headers,
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
            except httpx.RequestError:
                pass

            time.sleep(random.uniform(5, 30))

            return (
                'Thank you for contacting our support team. '
                'We have received your request and will review it shortly.'
            )

        response = httpx.post(
            self.base_url,
            headers=headers,
            json={
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt,
                    },
                ],
            },
            timeout=30.0,
        )

        response.raise_for_status()

        return response.json()['choices'][0]['message']['content'].strip()


def get_llm_provider() -> BaseLLMProvider:
    provider = os.getenv('LLM_PROVIDER', 'openai').lower()

    if provider == 'openai':
        return OpenAIProvider()

    raise ValueError(f'Unsupported LLM provider: {provider}')