from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.assistant.models import Draft
from apps.integrations.helpdesk import HelpdeskClient
from apps.integrations.models import OutboxEvent
import httpx


TASK_MAPPING = {
    'process_ticket': 'apps.assistant.tasks.process_ticket',
}


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_approved_draft(self, draft_id: int):
    try:
        draft = Draft.objects.select_related('ticket').get(pk=draft_id)

        if draft.status == Draft.Status.SENT:
            return

        if draft.status != Draft.Status.APPROVED:
            return

        client = HelpdeskClient()

        client.send_reply(
            reply_url=draft.ticket.reply_url,
            ticket_id=draft.ticket.external_id,
            message=draft.content,
            idempotency_key=draft.idempotency_key,
        )

        Draft.objects.filter(
            pk=draft.pk,
            status=Draft.Status.APPROVED,
        ).update(
            status=Draft.Status.SENT,
            sent_at=timezone.now(),
        )

    except Draft.DoesNotExist:
        return

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code >= 500:
            raise self.retry(exc=exc)

        raise

    except (httpx.TimeoutException, httpx.TransportError) as exc:
        raise self.retry(exc=exc)


@shared_task
def dispatch_outbox_events(batch_size=50):
    now = timezone.now()

    with transaction.atomic():
        events = list(
            OutboxEvent.objects.select_for_update(skip_locked=True)
            .filter(
                Q(status=OutboxEvent.Status.PENDING)
                | Q(
                    status=OutboxEvent.Status.PROCESSING,
                    locked_until__lte=now,
                )
            )
            .filter(available_at__lte=now)
            .order_by('created_at')[:batch_size]
        )

        for event in events:
            event.status = OutboxEvent.Status.PROCESSING
            event.locked_until = now + timedelta(minutes=2)
            event.attempts += 1

        OutboxEvent.objects.bulk_update(
            events,
            ['status', 'locked_until', 'attempts'],
        )

    for event in events:
        try:
            task_name = TASK_MAPPING[event.event_type]

            from config.celery import app

            app.send_task(task_name, kwargs=event.payload)

            with transaction.atomic():
                locked_event = OutboxEvent.objects.select_for_update().get(
                    pk=event.pk
                )
                locked_event.status = OutboxEvent.Status.PUBLISHED
                locked_event.published_at = timezone.now()
                locked_event.locked_until = None
                locked_event.last_error = ''
                locked_event.save(
                    update_fields=[
                        'status',
                        'published_at',
                        'locked_until',
                        'last_error',
                    ]
                )

        except Exception as exc:
            with transaction.atomic():
                locked_event = OutboxEvent.objects.select_for_update().get(
                    pk=event.pk
                )
                locked_event.status = OutboxEvent.Status.PENDING
                locked_event.available_at = timezone.now() + timedelta(
                    seconds=min(2 ** event.attempts, 300)
                )
                locked_event.locked_until = None
                locked_event.last_error = str(exc)
                locked_event.save(
                    update_fields=[
                        'status',
                        'available_at',
                        'locked_until',
                        'last_error',
                    ]
                )