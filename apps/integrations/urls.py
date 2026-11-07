from django.urls import path

from apps.integrations.mock_helpdesk import MockHelpdeskReplyView

urlpatterns = [
    path(
        'tickets/<str:ticket_id>/replies/',
        MockHelpdeskReplyView.as_view(),
        name='mock-helpdesk-reply',
    ),
]