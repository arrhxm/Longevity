from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clients", "0004_clientprofile_assigned_dietitian"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientprofile",
            name="dietary_preference",
            field=models.CharField(
                blank=True,
                choices=[
                    ("VEGETARIAN", "Vegetarian"),
                    ("VEGETARIAN_EGGS", "Vegetarian + Eggs"),
                    ("NON_VEGETARIAN", "Non-Vegetarian"),
                    ("VEGAN", "Vegan"),
                ],
                max_length=30,
            ),
        ),
    ]
