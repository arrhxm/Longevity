import datetime

from django.utils import timezone

from .models import Appointment


def find_conflicting_appointment(date, time, duration_minutes, exclude_id=None):
    """
    Returns the first SCHEDULED appointment that overlaps with the given
    date/time/duration window, or None if there's no conflict.

    The platform currently has a single dietitian, so appointments are
    compared globally (there's no per-dietitian scoping) -- two
    appointments can never be handled by the same person at overlapping
    times.
    """
    start = datetime.datetime.combine(date, time)
    end = start + datetime.timedelta(minutes=duration_minutes or 0)

    candidates = Appointment.objects.filter(
        date=date,
        status=Appointment.Status.SCHEDULED,
    ).select_related("client__user")

    if exclude_id:
        candidates = candidates.exclude(id=exclude_id)

    for candidate in candidates:
        candidate_start = datetime.datetime.combine(
            candidate.date, candidate.time
        )
        candidate_end = candidate_start + datetime.timedelta(
            minutes=candidate.duration_minutes or 0
        )

        overlaps = start < candidate_end and candidate_start < end

        if overlaps:
            return candidate

    return None


def send_appointment_reminders():
    """
    Sends a reminder notification to every client whose SCHEDULED
    appointment falls tomorrow and hasn't already been reminded.

    Intended to be run once a day via cron / a scheduled task (see the
    ``send_appointment_reminders`` management command), the same way
    ``sync_memberships`` handles membership housekeeping.
    """
    from notifications.models import Notification

    tomorrow = timezone.localdate() + datetime.timedelta(days=1)

    appointments = (
        Appointment.objects
        .filter(
            status=Appointment.Status.SCHEDULED,
            date=tomorrow,
            reminder_sent=False,
        )
        .select_related("client__user")
    )

    reminded_count = 0

    for appointment in appointments:
        Notification.objects.create(
            user=appointment.client.user,
            notification_type=Notification.NotificationType.APPOINTMENT,
            title="Appointment Reminder",
            message=(
                f"Reminder: you have an appointment tomorrow, "
                f"{appointment.date}, at "
                f"{appointment.time.strftime('%I:%M %p')}."
            ),
        )

        appointment.reminder_sent = True
        appointment.save(update_fields=["reminder_sent"])

        reminded_count += 1

    return {"reminded_count": reminded_count}
