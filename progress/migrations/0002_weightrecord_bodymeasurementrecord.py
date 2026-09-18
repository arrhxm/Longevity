# Generated manually for the client-owned progress tracking redesign.

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("clients", "0001_initial"),
        ("progress", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WeightRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(default=django.utils.timezone.localdate)),
                ("weight", models.DecimalField(decimal_places=2, max_digits=6)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("client", models.ForeignKey(limit_choices_to={"role": "CLIENT"}, on_delete=django.db.models.deletion.CASCADE, related_name="weight_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-date", "-id"],
            },
        ),
        migrations.CreateModel(
            name="BodyMeasurementRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(default=django.utils.timezone.localdate)),
                ("neck", models.DecimalField(decimal_places=2, max_digits=6)),
                ("chest", models.DecimalField(decimal_places=2, max_digits=6)),
                ("shoulder", models.DecimalField(decimal_places=2, max_digits=6)),
                ("stomach_navel", models.DecimalField(decimal_places=2, max_digits=6)),
                ("stomach_above_navel", models.DecimalField(decimal_places=2, max_digits=6)),
                ("stomach_below_navel", models.DecimalField(decimal_places=2, max_digits=6)),
                ("arms_flexed", models.DecimalField(decimal_places=2, max_digits=6)),
                ("waist", models.DecimalField(decimal_places=2, max_digits=6)),
                ("thighs_mid_above_knee", models.DecimalField(decimal_places=2, max_digits=6)),
                ("front_photo", models.FileField(blank=True, null=True, upload_to="progress/%Y/%m/%d/front/", validators=[django.core.validators.FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])])),
                ("side_photo", models.FileField(blank=True, null=True, upload_to="progress/%Y/%m/%d/side/", validators=[django.core.validators.FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])])),
                ("back_photo", models.FileField(blank=True, null=True, upload_to="progress/%Y/%m/%d/back/", validators=[django.core.validators.FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])])),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("client", models.ForeignKey(limit_choices_to={"role": "CLIENT"}, on_delete=django.db.models.deletion.CASCADE, related_name="body_measurement_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-date", "-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="weightrecord",
            constraint=models.UniqueConstraint(fields=("client", "date"), name="unique_weight_record_per_day"),
        ),
        migrations.AddConstraint(
            model_name="bodymeasurementrecord",
            constraint=models.UniqueConstraint(fields=("client", "date"), name="unique_measurement_record_per_day"),
        ),
    ]
