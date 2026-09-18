from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nutrition", "0005_foodlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="foodlog",
            name="prescribed_meals",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
