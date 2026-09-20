from django.conf import settings
from django.db import models
from clients.models import ClientProfile
from payments.models import Membership


class Query(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        ANSWERED = "ANSWERED", "Answered"
        CLOSED = "CLOSED", "Closed"

    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name="queries")
    membership = models.ForeignKey(Membership, on_delete=models.PROTECT, related_name="queries")
    dietitian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="client_queries",
        limit_choices_to={"role": "DIETITIAN"},
    )
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return f"{self.subject} - {self.client}"


class QueryMessage(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="query_messages")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"Message #{self.pk} - {self.query.subject}"
