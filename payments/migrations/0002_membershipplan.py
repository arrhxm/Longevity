from django.db import migrations, models


def seed_india_plans(apps, schema_editor):
    MembershipPlan = apps.get_model("payments", "MembershipPlan")
    plans = [
        ("3 Months", 3, "7999.00", 1),
        ("6 Months", 6, "14999.00", 2),
        ("9 Months", 9, "16999.00", 3),
        ("12 Months", 12, "19999.00", 4),
    ]
    for name, duration, amount, order in plans:
        MembershipPlan.objects.create(
            name=name,
            duration_months=duration,
            amount=amount,
            country="IN",
            display_order=order,
        )


def remove_seeded_india_plans(apps, schema_editor):
    MembershipPlan = apps.get_model("payments", "MembershipPlan")
    MembershipPlan.objects.filter(country="IN", duration_months__in=[3, 6, 9, 12]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MembershipPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("duration_months", models.PositiveSmallIntegerField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("country", models.CharField(default="IN", max_length=10)),
                ("is_active", models.BooleanField(default=True)),
                ("display_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["display_order", "duration_months", "id"]},
        ),
        migrations.AddConstraint(
            model_name="membershipplan",
            constraint=models.UniqueConstraint(
                fields=("country", "duration_months"),
                name="unique_plan_duration_country",
            ),
        ),
        migrations.RunPython(seed_india_plans, remove_seeded_india_plans),
    ]
