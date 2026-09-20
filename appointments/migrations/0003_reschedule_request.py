from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_registrationotp"),
        ("appointments", "0002_appointment_reminder_sent"),
        ("clients", "0004_clientprofile_assigned_dietitian"),
    ]

    operations = [
        migrations.CreateModel(
            name="RescheduleRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("original_date", models.DateField()),
                ("original_time", models.TimeField()),
                ("requested_date", models.DateField()),
                ("requested_time", models.TimeField()),
                ("reason", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("APPROVED", "Approved"), ("DECLINED", "Declined")], default="PENDING", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("handled_at", models.DateTimeField(blank=True, null=True)),
                ("appointment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reschedule_requests", to="appointments.appointment")),
                ("client", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reschedule_requests", to="clients.clientprofile")),
                ("handled_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="handled_reschedule_requests", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
