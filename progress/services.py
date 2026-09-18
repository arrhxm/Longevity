from datetime import timedelta

from django.utils import timezone

from notifications.models import Notification

from .models import BodyMeasurementRecord, WeightRecord


def _create_reminder(user, title, message):
    recent = Notification.objects.filter(
        user=user,
        notification_type=Notification.NotificationType.PROGRESS,
        title=title,
        created_at__gte=timezone.now() - timedelta(days=1),
    ).exists()
    if not recent:
        Notification.objects.create(
            user=user,
            notification_type=Notification.NotificationType.PROGRESS,
            title=title,
            message=message,
        )


def send_progress_reminder_for_client(user):
    today = timezone.localdate()

    last_weight = (
        WeightRecord.objects.filter(client=user)
        .order_by("-date")
        .first()
    )
    weight_due = not last_weight or today >= last_weight.date + timedelta(days=7)

    if weight_due:
        _create_reminder(
            user,
            "Weekly Weight Update Due",
            "Your weekly weight update is due. Please add your current weight in your Progress section.",
        )

    last_measurement = (
        BodyMeasurementRecord.objects.filter(client=user)
        .order_by("-date")
        .first()
    )
    measurement_due = (
        not last_measurement
        or today >= last_measurement.date + timedelta(days=30)
    )

    if measurement_due:
        _create_reminder(
            user,
            "Monthly Measurements Due",
            "Your 30-day body measurement update is due. Please update your measurements and optional progress photos.",
        )

    return {
        "weight_due": weight_due,
        "measurement_due": measurement_due,
        "last_weight": last_weight,
        "last_measurement": last_measurement,
    }


def send_progress_reminders():
    from accounts.models import User

    clients = User.objects.filter(role=User.Role.CLIENT)
    for client in clients:
        send_progress_reminder_for_client(client)
