from django.db import models


class Ticket(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        PROCESSING = 'processing', 'Processing'
        WAITING = 'waiting', 'Waiting'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    external_id = models.CharField(
        max_length=255,
        unique=True,
    )
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True)
    reply_url = models.URLField(max_length=1000, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    def __str__(self):
        return f'{self.external_id}: {self.subject}'