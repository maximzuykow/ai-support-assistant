from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import OutboxEvent


TASK_MAPPING = {
    'process_ticket': 'apps.assistant.tasks.process_ticket',
}


@shared_task
def dispatch_outbox_events(batch_size=50):
    now = timezone.now()

    with transaction.atomic():
        events = list(
            OutboxEvent.objects
            .select_for_update(skip_locked=True)
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

            app.send_task(
                task_name,
                kwargs=event.payload,
            )

            with transaction.atomic():
                locked_event = OutboxEvent.objects.select_for_update().get(
                    pk=event.pk,
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
                    ],
                )

        except Exception as exc:
            with transaction.atomic():
                locked_event = OutboxEvent.objects.select_for_update().get(
                    pk=event.pk,
                )

                locked_event.status = OutboxEvent.Status.PENDING
                locked_event.available_at = (
                    timezone.now()
                    + timedelta(seconds=min(2 ** event.attempts, 300))
                )
                locked_event.locked_until = None
                locked_event.last_error = str(exc)

                locked_event.save(
                    update_fields=[
                        'status',
                        'available_at',
                        'locked_until',
                        'last_error',
                    ],
                )