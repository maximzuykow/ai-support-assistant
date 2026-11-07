from django.db import models

from apps.tickets.models import Ticket


class Draft(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        SENT = 'sent', 'Sent'

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='drafts',
    )

    content = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Draft'
        verbose_name_plural = 'Drafts'

    def __str__(self):
        return f'Draft #{self.pk} for ticket #{self.ticket_id}'