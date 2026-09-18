from django.db import migrations, models
from django.db.models import Q


def deduplicate_active_memberships(apps, schema_editor):
    Membership = apps.get_model("payments", "Membership")

    client_ids = (
        Membership.objects
        .filter(status="ACTIVE")
        .values_list("client_id", flat=True)
        .distinct()
    )

    for client_id in client_ids:
        active = list(
            Membership.objects
            .filter(client_id=client_id, status="ACTIVE")
            .order_by("-created_at", "-id")
        )
        # Keep the most recently created active membership and preserve older
        # records as historical cancelled records rather than deleting them.
        for membership in active[1:]:
            membership.status = "CANCELLED"
            membership.save(update_fields=["status"])


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0003_membership_enrollment"),
    ]

    operations = [
        migrations.RunPython(
            deduplicate_active_memberships,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="membership",
            constraint=models.UniqueConstraint(
                fields=("client",),
                condition=Q(status="ACTIVE"),
                name="one_active_membership_per_client",
            ),
        ),
    ]
