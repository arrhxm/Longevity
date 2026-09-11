from django.conf import settings
from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        PAYMENT_DUE = "PAYMENT_DUE", "Payment Due"
        PAYMENT_RECEIVED = "PAYMENT_RECEIVED", "Payment Received"
        APPOINTMENT = "APPOINTMENT", "Appointment"
        DIET_PLAN = "DIET_PLAN", "Diet Plan"
        PROGRESS = "PROGRESS", "Progress"
        GENERAL = "GENERAL", "General"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"