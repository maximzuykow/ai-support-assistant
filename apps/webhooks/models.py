from django.db import models


class WebhookEvent(models.Model):
    event_id = models.CharField(
        max_length=255,
        unique=True,
    )
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Status(models.TextChoices):
        RECEIVED = 'received', 'Received'
        PROCESSING = 'processing', 'Processing'
        PROCESSED = 'processed', 'Processed'
        FAILED = 'failed', 'Failed'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
    )

    class Meta:
        ordering = ['-received_at']
        verbose_name = 'Webhook event'
        verbose_name_plural = 'Webhook events'

    def __str__(self):
        return f'{self.event_id} ({self.status})'