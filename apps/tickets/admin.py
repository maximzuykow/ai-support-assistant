from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'external_id',
        'customer_name',
        'customer_email',
        'subject',
        'status',
        'created_at',
    )

    list_filter = ('status', 'created_at')
    search_fields = (
        'external_id',
        'customer_name',
        'customer_email',
        'subject',
        'message',
    )

    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)