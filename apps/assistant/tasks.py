from celery import shared_task
from django.db import transaction

from apps.assistant.models import Draft
from apps.assistant.services import generate_draft
from apps.tickets.models import Ticket
from apps.webhooks.models import WebhookEvent
from apps.assistant.rate_limiter import RateLimitExceeded


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def process_ticket(self, webhook_event_id: int):
    try:
        with transaction.atomic():
            event = WebhookEvent.objects.select_for_update().get(
                pk=webhook_event_id,
            )

            payload = event.payload
            ticket_data = payload.get('ticket', payload)

            external_id = ticket_data.get(
                'ticket_id',
                ticket_data.get('external_id'),
            )

            if not external_id:
                raise ValueError('Webhook payload has no ticket_id')

            ticket, created = Ticket.objects.get_or_create(
            external_id=str(external_id),
            defaults={
                'customer_name': ticket_data.get('customer_name', 'Unknown'),
                'customer_email': ticket_data.get('customer_email', ''),
                'subject': ticket_data.get('subject', 'No subject'),
                'message': ticket_data.get('message', ''),
                'reply_url': ticket_data.get('reply_url', ''),
            },
        )

        if not ticket.reply_url and ticket_data.get('reply_url'):
            ticket.reply_url = ticket_data['reply_url']
            ticket.save(update_fields=['reply_url'])

        idempotency_key = f'ticket:{ticket.pk}:initial-draft'

        if Draft.objects.filter(idempotency_key=idempotency_key).exists():
            return

        content = generate_draft(ticket)

        Draft.objects.get_or_create(
            idempotency_key=idempotency_key,
            defaults={
                'ticket': ticket,
                'content': content,
            },
        )

    except WebhookEvent.DoesNotExist:
        return
    except RateLimitExceeded as exc:
        raise self.retry(
            exc=exc,
            countdown=exc.retry_after,
        )
    except Exception as exc:
        raise self.retry(exc=exc)