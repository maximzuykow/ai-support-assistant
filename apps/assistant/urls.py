from django.urls import path

from .views import TicketDetailView, TicketListView

urlpatterns = [
    path('tickets/', TicketListView.as_view(), name='ticket-list'),
    path(
        'tickets/<int:pk>/',
        TicketDetailView.as_view(),
        name='ticket-detail',
    ),
]