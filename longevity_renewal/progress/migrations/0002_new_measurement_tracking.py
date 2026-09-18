from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("progress", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="progressrecord",
            name="record_type",
            field=models.CharField(choices=[("INITIAL", "Initial Measurement"), ("WEEKLY_WEIGHT", "Weekly Weight"), ("MONTHLY_MEASUREMENT", "Monthly Measurement"), ("DIETITIAN_UPDATE", "Dietitian Update")], default="DIETITIAN_UPDATE", max_length=30),
        ),
        migrations.RemoveField(model_name="progressrecord", name="body_fat_percentage"),
        migrations.RemoveField(model_name="progressrecord", name="hips"),
        migrations.AddField(model_name="progressrecord", name="neck_circumference", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
        migrations.AddField(model_name="progressrecord", name="chest_circumference", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
        migrations.AddField(model_name="progressrecord", name="shoulder_circumference", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
        migrations.AddField(model_name="progressrecord", name="stomach_on_naval", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
        migrations.AddField(model_name="progressrecord", name="stomach_above_naval", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
        migrations.AddField(model_name="progressrecord", name="stomach_below_naval", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
        migrations.AddField(model_name="progressrecord", name="arms_flexed", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
        migrations.AddField(model_name="progressrecord", name="thighs_mid_section", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
    ]
