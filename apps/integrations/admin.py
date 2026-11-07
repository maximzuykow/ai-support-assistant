from django.contrib import admin

from .models import OutboxEvent


@admin.register(OutboxEvent)
class OutboxEventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'event_type',
        'deduplication_key',
        'status',
        'attempts',
        'available_at',
        'published_at',
    )

    list_filter = ('status', 'event_type', 'created_at')
    search_fields = ('event_type', 'deduplication_key')
    readonly_fields = ('created_at', 'published_at')
    ordering = ('created_at',)