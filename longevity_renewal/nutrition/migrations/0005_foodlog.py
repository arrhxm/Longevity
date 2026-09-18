from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("nutrition", "0004_remove_dietplan_plan_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="FoodLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("photo", models.FileField(upload_to="food_logs/%Y/%m/%d/", validators=[django.core.validators.FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])])),
                ("note", models.TextField(blank=True)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("review_status", models.CharField(choices=[("PENDING", "Pending"), ("FOLLOWED", "Followed"), ("PARTIALLY_FOLLOWED", "Partially followed"), ("NOT_FOLLOWED", "Not followed")], default="PENDING", max_length=30)),
                ("dietitian_feedback", models.TextField(blank=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("client", models.ForeignKey(limit_choices_to={"role": "CLIENT"}, on_delete=django.db.models.deletion.CASCADE, related_name="food_logs", to=settings.AUTH_USER_MODEL)),
                ("diet_plan", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="food_logs", to="nutrition.dietplan")),
                ("option_section", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="food_logs", to="nutrition.optionsection")),
                ("section", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="food_logs", to="nutrition.section")),
            ],
            options={"ordering": ["-uploaded_at"]},
        ),
    ]
