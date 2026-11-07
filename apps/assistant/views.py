from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assistant.models import Draft
from apps.assistant.serializers import TicketSerializer
from apps.tickets.models import Ticket


class TicketListView(generics.ListAPIView):
    queryset = Ticket.objects.prefetch_related('drafts').all()
    serializer_class = TicketSerializer
    permission_classes = [IsAdminUser]


class TicketDetailView(generics.RetrieveAPIView):
    queryset = Ticket.objects.prefetch_related('drafts').all()
    serializer_class = TicketSerializer
    permission_classes = [IsAdminUser]


class DraftApprovalView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        draft = get_object_or_404(
            Draft.objects.select_related('ticket'),
            pk=pk,
        )

        if draft.status != Draft.Status.PENDING:
            return Response(
                {'detail': 'Draft is not pending.'},
                status=status.HTTP_409_CONFLICT,
            )

        draft.status = Draft.Status.APPROVED
        draft.approved_at = timezone.now()
        draft.save(update_fields=['status', 'approved_at'])

        return Response({
            'detail': 'Draft approved.',
            'draft_id': draft.pk,
            'status': draft.status,
        })


class DraftRejectionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        draft = get_object_or_404(Draft, pk=pk)

        if draft.status != Draft.Status.PENDING:
            return Response(
                {'detail': 'Draft is not pending.'},
                status=status.HTTP_409_CONFLICT,
            )

        draft.status = Draft.Status.REJECTED
        draft.save(update_fields=['status'])

        return Response({
            'detail': 'Draft rejected.',
            'draft_id': draft.pk,
            'status': draft.status,
        })