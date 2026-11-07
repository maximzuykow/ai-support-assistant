from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.assistant.models import Draft
from apps.integrations.tasks import send_approved_draft
from apps.tickets.models import Ticket


@staff_member_required
def operator_dashboard(request):
    tickets = (
        Ticket.objects
        .prefetch_related('drafts')
        .order_by('-created_at')
    )

    return render(
        request,
        'assistant/operator_dashboard.html',
        {'tickets': tickets},
    )


@staff_member_required
@require_POST
def approve_draft(request, pk):
    with transaction.atomic():
        draft = get_object_or_404(
            Draft.objects.select_for_update(),
            pk=pk,
        )

        if draft.status != Draft.Status.PENDING:
            messages.warning(request, 'This draft is no longer pending.')
            return redirect('operator-dashboard')

        draft.status = Draft.Status.APPROVED
        draft.approved_at = timezone.now()
        draft.save(update_fields=['status', 'approved_at'])

        transaction.on_commit(
            lambda: send_approved_draft.delay(draft.pk)
        )

    messages.success(request, 'Draft approved and queued for sending.')
    return redirect('operator-dashboard')


@staff_member_required
@require_POST
def reject_draft(request, pk):
    with transaction.atomic():
        draft = get_object_or_404(
            Draft.objects.select_for_update(),
            pk=pk,
        )

        if draft.status != Draft.Status.PENDING:
            messages.warning(request, 'This draft is no longer pending.')
            return redirect('operator-dashboard')

        draft.status = Draft.Status.REJECTED
        draft.save(update_fields=['status'])

    messages.success(request, 'Draft rejected.')
    return redirect('operator-dashboard')