import os

import httpx


class HelpdeskClient:
    def __init__(self):
        self.base_url = os.getenv('HELPDESK_API_URL')
        self.api_key = os.getenv('HELPDESK_API_KEY')

    def send_reply(
        self,
        ticket_id: str,
        message: str,
        idempotency_key: str,
    ) -> dict:
        if not self.base_url:
            raise ValueError('HELPDESK_API_URL is not configured')

        response = httpx.post(
            f'{self.base_url.rstrip("/")}/tickets/{ticket_id}/replies/',
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Idempotency-Key': idempotency_key,
            },
            json={'message': message},
            timeout=15.0,
        )

        response.raise_for_status()
        return response.json()