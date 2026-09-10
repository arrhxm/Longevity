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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - {self.date} {self.time}"