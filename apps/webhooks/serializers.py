from rest_framework import serializers


class WebhookSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=255)
    event_type = serializers.CharField(max_length=100)
    ticket = serializers.DictField()