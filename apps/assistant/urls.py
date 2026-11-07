from django.urls import path

from .views import (
    DraftApprovalView,
    DraftRejectionView,
    TicketDetailView,
    TicketListView,
)

urlpatterns = [
    path('tickets/', TicketListView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path(
        'drafts/<int:pk>/approve/',
        DraftApprovalView.as_view(),
        name='draft-approve',
    ),
    path(
        'drafts/<int:pk>/reject/',
        DraftRejectionView.as_view(),
        name='draft-reject',
    ),
]