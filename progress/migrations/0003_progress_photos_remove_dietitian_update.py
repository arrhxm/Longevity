from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("progress", "0002_new_measurement_tracking")]

    operations = [
        migrations.AlterField(
            model_name="progressrecord",
            name="record_type",
            field=models.CharField(
                choices=[
                    ("INITIAL", "Initial Measurement"),
                    ("WEEKLY_WEIGHT", "Weekly Weight"),
                    ("MONTHLY_MEASUREMENT", "Monthly Measurement"),
                ],
                default="INITIAL",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="progressrecord",
            name="front_photo",
            field=models.ImageField(blank=True, null=True, upload_to="progress_photos/front/"),
        ),
        migrations.AddField(
            model_name="progressrecord",
            name="side_photo",
            field=models.ImageField(blank=True, null=True, upload_to="progress_photos/side/"),
        ),
        migrations.AddField(
            model_name="progressrecord",
            name="back_photo",
            field=models.ImageField(blank=True, null=True, upload_to="progress_photos/back/"),
        ),
    ]
