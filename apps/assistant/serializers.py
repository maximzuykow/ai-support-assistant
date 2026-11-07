from rest_framework import serializers

from apps.assistant.models import Draft
from apps.tickets.models import Ticket


class DraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Draft
        fields = (
            'id',
            'ticket',
            'content',
            'status',
            'created_at',
            'approved_at',
            'sent_at',
        )
        read_only_fields = fields


class TicketSerializer(serializers.ModelSerializer):
    drafts = DraftSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = (
            'id',
            'external_id',
            'customer_name',
            'customer_email',
            'subject',
            'message',
            'status',
            'created_at',
            'updated_at',
            'drafts',
        )