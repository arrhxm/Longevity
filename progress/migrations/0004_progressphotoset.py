from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("progress", "0003_progress_photos_remove_dietitian_update"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProgressPhotoSet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(auto_now_add=True)),
                ("front_photo", models.ImageField(blank=True, null=True, upload_to="progress_photos/front/")),
                ("side_photo", models.ImageField(blank=True, null=True, upload_to="progress_photos/side/")),
                ("back_photo", models.ImageField(blank=True, null=True, upload_to="progress_photos/back/")),
                ("client", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progress_photo_sets", to="clients.clientprofile")),
            ],
            options={"ordering": ["-date", "-id"]},
        ),
    ]
