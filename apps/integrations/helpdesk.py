import os

import httpx


class HelpdeskClient:
    def __init__(self):
        self.api_key = os.getenv('HELPDESK_API_KEY')

    def send_reply(
        self,
        reply_url: str,
        ticket_id: str,
        message: str,
        idempotency_key: str,
    ) -> dict:
        if not reply_url:
            raise ValueError('Reply URL is not configured')

        if not self.api_key:
            raise ValueError('HELPDESK_API_KEY is not configured')

        response = httpx.post(
            reply_url,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Idempotency-Key': idempotency_key,
            },
            json={
                'ticket_id': ticket_id,
                'message': message,
            },
            timeout=15.0,
        )

        response.raise_for_status()
        return response.json()