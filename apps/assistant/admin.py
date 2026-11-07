from django.contrib import admin

from .models import Draft


@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ticket',
        'status',
        'created_at',
        'approved_at',
        'sent_at',
    )

    list_filter = ('status', 'created_at')
    search_fields = (
        'ticket__external_id',
        'ticket__customer_name',
        'content',
        'idempotency_key',
    )

    readonly_fields = (
        'created_at',
        'approved_at',
        'sent_at',
    )

    ordering = ('-created_at',)