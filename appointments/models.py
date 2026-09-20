from django.db import models
from clients.models import ClientProfile


class Appointment(models.Model):

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No Show"

    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    date = models.DateField()

    time = models.TimeField()

    duration_minutes = models.PositiveIntegerField(
        default=30
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )

    reason = models.CharField(
        max_length=255,
        blank=True,
    )

    notes = models.TextField(blank=True)

    reminder_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - {self.date} {self.time}"

class RescheduleRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        DECLINED = "DECLINED", "Declined"

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="reschedule_requests")
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name="reschedule_requests")
    original_date = models.DateField()
    original_time = models.TimeField()
    requested_date = models.DateField()
    requested_time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    handled_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="handled_reschedule_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    handled_at = models.DateTimeField(null=True, blank=True)
