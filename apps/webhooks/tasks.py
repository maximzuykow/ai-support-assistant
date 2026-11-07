from celery import shared_task
from django.utils import timezone

from .models import WebhookEvent


@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=10,
)
def process_webhook_event(self, event_id: int):
    try:
        event = WebhookEvent.objects.get(pk=event_id)
    except WebhookEvent.DoesNotExist:
        return

    if event.status == WebhookEvent.Status.PROCESSED:
        return

    event.status = WebhookEvent.Status.PROCESSING
    event.save(update_fields=['status'])

    try:
        from apps.integrations.models import OutboxEvent

        OutboxEvent.objects.get_or_create(
            deduplication_key=f'process-ticket:{event.event_id}',
            defaults={
                'event_type': 'process_ticket',
                'payload': {
                    'webhook_event_id': event.pk,
                },
                'available_at': timezone.now(),
            },
        )

        event.status = WebhookEvent.Status.PROCESSED
        event.processed_at = timezone.now()
        event.save(update_fields=['status', 'processed_at'])

    except Exception as exc:
        event.status = WebhookEvent.Status.FAILED
        event.save(update_fields=['status'])

        raise self.retry(exc=exc)