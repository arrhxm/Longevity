from datetime import timedelta

from django.utils import timezone

from notifications.models import Notification

from .models import Membership


EXPIRING_SOON_WINDOW_DAYS = 7


def sync_membership_statuses():
    """
    Housekeeping routine for memberships:

    1. Any ACTIVE membership whose end_date has already passed is
       transitioned to EXPIRED.
    2. Any ACTIVE membership expiring within the next
       ``EXPIRING_SOON_WINDOW_DAYS`` days gets a one-time "expiring soon"
       notification sent to the client (deduplicated so it is only ever
       sent once per membership).

    This is called opportunistically from dashboard/list views so the
    data is always fresh even without a scheduled task configured, but it
    can also be run explicitly (e.g. from a daily cron job) via the
    ``sync_memberships`` management command.

    Returns a dict summarising what happened, mostly useful for the
    management command's output.
    """
    today = timezone.localdate()

    expired_count = Membership.objects.filter(
        status=Membership.Status.ACTIVE,
        end_date__lt=today,
    ).update(status=Membership.Status.EXPIRED)

    soon_cutoff = today + timedelta(days=EXPIRING_SOON_WINDOW_DAYS)

    expiring_soon = (
        Membership.objects
        .filter(
            status=Membership.Status.ACTIVE,
            end_date__gte=today,
            end_date__lte=soon_cutoff,
        )
        .select_related("client__user")
    )

    notified_count = 0

    for membership in expiring_soon:
        title = f"Membership Expiring Soon: {membership.name}"

        already_notified = Notification.objects.filter(
            user=membership.client.user,
            notification_type=Notification.NotificationType.PAYMENT_DUE,
            title=title,
        ).exists()

        if already_notified:
            continue

        days_left = (membership.end_date - today).days

        Notification.objects.create(
            user=membership.client.user,
            notification_type=Notification.NotificationType.PAYMENT_DUE,
            title=title,
            message=(
                f"Your membership '{membership.name}' expires on "
                f"{membership.end_date.strftime('%d %b %Y')} "
                f"({days_left} day{'s' if days_left != 1 else ''} left). "
                f"Please renew to continue uninterrupted service."
            ),
        )

        notified_count += 1

    return {
        "expired_count": expired_count,
        "notified_count": notified_count,
    }
