from django.db import IntegrityError, transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.integrations.models import OutboxEvent
from apps.webhooks.models import WebhookEvent
from .serializers import WebhookSerializer


class WebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = WebhookSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data

        try:
            with transaction.atomic():
                event, created = WebhookEvent.objects.get_or_create(
                    event_id=data['event_id'],
                    defaults={
                        'event_type': data['event_type'],
                        'payload': data,
                    },
                )

                if not created:
                    return Response(
                        {'detail': 'Event already received.'},
                        status=status.HTTP_200_OK,
                    )

                OutboxEvent.objects.create(
                    event_type='process_ticket',
                    deduplication_key=f'webhook:{event.event_id}',
                    payload={'webhook_event_id': event.pk},
                    available_at=event.received_at,
                )

        except IntegrityError:
            return Response(
                {'detail': 'Event already received.'},
                status=status.HTTP_200_OK,
            )

        return Response(
            {'detail': 'Webhook accepted.', 'event_id': event.event_id},
            status=status.HTTP_202_ACCEPTED,
        )