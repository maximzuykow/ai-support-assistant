from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

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