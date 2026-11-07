from rest_framework import serializers


class WebhookSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=255)
    ticket_id = serializers.CharField(max_length=255)
    customer_email = serializers.EmailField()
    message = serializers.CharField()
    reply_url = serializers.URLField()