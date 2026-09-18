from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("clients", "0002_rename_health_goals_clientprofile_health_goal"),
        ("payments", "0002_membershipplan"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientprofile",
            name="gender",
            field=models.CharField(blank=True, choices=[("MALE", "Male"), ("FEMALE", "Female"), ("OTHER", "Other"), ("PREFER_NOT_TO_SAY", "Prefer not to say")], max_length=30),
        ),
        migrations.AddField(
            model_name="clientprofile",
            name="country",
            field=models.CharField(choices=[("IN", "India"), ("US", "United States"), ("GB", "United Kingdom"), ("AE", "United Arab Emirates"), ("CA", "Canada"), ("AU", "Australia"), ("OTHER", "Other")], default="IN", max_length=10),
        ),
        migrations.AddField(model_name="clientprofile", name="state", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="clientprofile", name="city", field=models.CharField(blank=True, max_length=100)),
        migrations.AlterField(
            model_name="clientprofile",
            name="health_goal",
            field=models.CharField(blank=True, choices=[("WEIGHT_LOSS", "Weight Loss"), ("FAT_LOSS", "Fat Loss"), ("WEIGHT_GAIN", "Weight Gain"), ("MUSCLE_GAIN", "Muscle Gain"), ("GENERAL_FITNESS", "General Fitness"), ("HEALTHY_LIFESTYLE", "Healthy Lifestyle"), ("OTHER", "Other")], max_length=50),
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("PROFILE_COMPLETE", "Profile Complete"), ("PENDING_PAYMENT", "Pending Payment"), ("COMPLETED", "Completed"), ("CANCELLED", "Cancelled")], default="PROFILE_COMPLETE", max_length=30)),
                ("enrolled_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("client", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="enrollment", to="clients.clientprofile")),
                ("membership_plan", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="payments.membershipplan")),
            ],
        ),
    ]
