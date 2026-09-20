from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0003_registrationotp"),
        ("clients", "0004_clientprofile_assigned_dietitian"),
        ("payments", "0004_one_active_membership"),
    ]

    operations = [
        migrations.CreateModel(
            name="Query",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(max_length=200)),
                ("status", models.CharField(choices=[("OPEN", "Open"), ("IN_PROGRESS", "In Progress"), ("ANSWERED", "Answered"), ("CLOSED", "Closed")], default="OPEN", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("client", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="queries", to="clients.clientprofile")),
                ("dietitian", models.ForeignKey(limit_choices_to={"role": "DIETITIAN"}, on_delete=django.db.models.deletion.PROTECT, related_name="client_queries", to=settings.AUTH_USER_MODEL)),
                ("membership", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="queries", to="payments.membership")),
            ],
            options={"ordering": ["-updated_at", "-id"]},
        ),
        migrations.CreateModel(
            name="QueryMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("query", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="queries.query")),
                ("sender", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="query_messages", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
    ]
