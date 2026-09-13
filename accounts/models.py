from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        DIETITIAN = "DIETITIAN", "Dietitian"
        CLIENT = "CLIENT", "Client"

    phone = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )

    def __str__(self):
        return f"{self.username} - {self.role}"


class RegistrationOTP(models.Model):
    phone = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"OTP for {self.phone}"