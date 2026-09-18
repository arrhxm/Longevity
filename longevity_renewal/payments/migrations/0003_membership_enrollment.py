from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0002_membershipplan"),
        ("clients", "0003_enrollment_profile_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="membership",
            name="enrollment",
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="membership", to="clients.enrollment"),
        ),
    ]
