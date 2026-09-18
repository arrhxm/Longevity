from django.db import models
from clients.models import ClientProfile


class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    duration_months = models.PositiveSmallIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    country = models.CharField(max_length=10, default="IN")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "duration_months", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["country", "duration_months"],
                name="unique_plan_duration_country",
            )
        ]

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"


class Membership(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"
        CANCELLED = "CANCELLED", "Cancelled"

    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    enrollment = models.OneToOneField(
        "clients.Enrollment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="membership",
    )
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} - {self.name}"


class Payment(models.Model):

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        UPI = "UPI", "UPI"
        CARD = "CARD", "Card"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PAID = "PAID", "Paid"
        PENDING = "PENDING", "Pending"
        PARTIAL = "PARTIAL", "Partial"

    membership = models.ForeignKey(
        Membership,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    payment_date = models.DateField()
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PAID,
    )
    transaction_id = models.CharField(
        max_length=200,
        blank=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.membership.client} - ₹{self.amount}"
