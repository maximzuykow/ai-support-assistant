import os
import secrets

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.integrations.models import MockHelpdeskReply


class MockHelpdeskReplyView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, ticket_id):
        api_key = os.getenv('HELPDESK_API_KEY', '')
        authorization = request.headers.get('Authorization', '')

        if not api_key or not secrets.compare_digest(
            authorization,
            f'Bearer {api_key}',
        ):
            return Response(
                {'detail': 'Unauthorized.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        message = request.data.get('message')
        idempotency_key = request.headers.get('Idempotency-Key')

        if not message or not idempotency_key:
            return Response(
                {'detail': 'Message and Idempotency-Key are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reply, created = MockHelpdeskReply.objects.get_or_create(
            idempotency_key=idempotency_key,
            defaults={
                'ticket_id': ticket_id,
                'message': message,
            },
        )

        return Response(
            {
                'id': reply.pk,
                'ticket_id': reply.ticket_id,
                'message': reply.message,
                'created': created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )