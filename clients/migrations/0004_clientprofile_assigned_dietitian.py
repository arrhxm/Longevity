from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_registrationotp"),
        ("clients", "0003_enrollment_profile_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientprofile",
            name="assigned_dietitian",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"role": "DIETITIAN"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_clients",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
