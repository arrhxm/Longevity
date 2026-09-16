from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def notification_list(request):
    notifications_qs = (
        Notification.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    paginator = Paginator(notifications_qs, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "notifications/notification_list.html",
        {
            "page_obj": page_obj,
        },
    )


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user,
    )

    if request.method == "POST":
        notification.is_read = True
        notification.save(update_fields=["is_read"])

    next_url = request.POST.get("next") or "notification_list"
    return redirect(next_url)


@login_required
def mark_all_notifications_read(request):
    if request.method == "POST":
        Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(is_read=True)

    next_url = request.POST.get("next") or "notification_list"
    return redirect(next_url)
