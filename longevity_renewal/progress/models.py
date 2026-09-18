from django.db import models
from clients.models import ClientProfile


class ProgressRecord(models.Model):
    class RecordType(models.TextChoices):
        INITIAL = "INITIAL", "Initial Measurement"
        WEEKLY_WEIGHT = "WEEKLY_WEIGHT", "Weekly Weight"
        MONTHLY_MEASUREMENT = "MONTHLY_MEASUREMENT", "Monthly Measurement"
        DIETITIAN_UPDATE = "DIETITIAN_UPDATE", "Dietitian Update"

    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="progress_records",
    )

    date = models.DateField()
    record_type = models.CharField(
        max_length=30,
        choices=RecordType.choices,
        default=RecordType.DIETITIAN_UPDATE,
    )
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    neck_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    chest_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    shoulder_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stomach_on_naval = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stomach_above_naval = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stomach_below_naval = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    arms_flexed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waist = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    thighs_mid_section = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.client} - {self.date}"
