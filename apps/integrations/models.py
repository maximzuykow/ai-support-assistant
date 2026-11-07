from django.db import models


class OutboxEvent(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        PUBLISHED = 'published', 'Published'

    event_type = models.CharField(max_length=100)

    deduplication_key = models.CharField(
        max_length=255,
        unique=True,
    )

    payload = models.JSONField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    attempts = models.PositiveIntegerField(default=0)
    available_at = models.DateTimeField()
    locked_until = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Outbox event'
        verbose_name_plural = 'Outbox events'
        indexes = [
            models.Index(
                fields=['status', 'available_at'],
                name='outbox_status_available_idx',
            ),
        ]

    def __str__(self):
        return f'{self.event_type}: {self.status}'

class MockHelpdeskReply(models.Model):
    ticket_id = models.CharField(max_length=255)
    message = models.TextField()
    idempotency_key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Reply for ticket {self.ticket_id}'