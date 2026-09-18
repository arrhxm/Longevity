def unread_notifications(request):
    """
    Makes ``unread_notification_count`` available in every template so
    the navbar bell badge can be shown without every view needing to
    fetch it manually.
    """
    user = getattr(request, "user", None)

    if not user or not user.is_authenticated:
        return {}

    from .models import Notification

    count = Notification.objects.filter(
        user=user,
        is_read=False,
    ).count()

    return {"unread_notification_count": count}
