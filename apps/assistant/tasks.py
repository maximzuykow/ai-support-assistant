from celery import shared_task
from django.db import transaction

from apps.tickets.models import Ticket
from apps.webhooks.models import WebhookEvent


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
                    'customer_name': ticket_data.get(
                        'customer_name',
                        'Unknown',
                    ),
                    'customer_email': ticket_data.get(
                        'customer_email',
                        '',
                    ),
                    'subject': ticket_data.get(
                        'subject',
                        'No subject',
                    ),
                    'message': ticket_data.get('message', ''),
                },
            )

            return {
                'ticket_id': ticket.pk,
                'created': created,
            }

    except WebhookEvent.DoesNotExist:
        return None

    except Exception as exc:
        raise self.retry(exc=exc)