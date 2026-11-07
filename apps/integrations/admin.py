from django.contrib import admin

from apps.integrations.models import MockHelpdeskReply, OutboxEvent


@admin.register(MockHelpdeskReply)
class MockHelpdeskReplyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ticket_id',
        'idempotency_key',
        'created_at',
    )
    search_fields = ('ticket_id', 'message', 'idempotency_key')
    readonly_fields = ('created_at',)


@admin.register(OutboxEvent)
class OutboxEventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'event_type',
        'status',
        'attempts',
        'available_at',
        'created_at',
    )
    list_filter = ('status', 'event_type')
    search_fields = ('deduplication_key',)
    readonly_fields = ('created_at',)