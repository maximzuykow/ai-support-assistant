from django.urls import path

from .operator_views import (
    approve_draft,
    operator_dashboard,
    reject_draft,
)
from .views import (
    DraftApprovalView,
    DraftRejectionView,
    TicketDetailView,
    TicketListView,
)

urlpatterns = [
    path('operator/', operator_dashboard, name='operator-dashboard'),
    path(
        'operator/drafts/<int:pk>/approve/',
        approve_draft,
        name='operator-approve',
    ),
    path(
        'operator/drafts/<int:pk>/reject/',
        reject_draft,
        name='operator-reject',
    ),

    path('tickets/', TicketListView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('drafts/<int:pk>/approve/', DraftApprovalView.as_view(), name='draft-approve'),
    path('drafts/<int:pk>/reject/', DraftRejectionView.as_view(), name='draft-reject'),
]