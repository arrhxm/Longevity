from django.core.management.base import BaseCommand

from payments.services import sync_membership_statuses


class Command(BaseCommand):
    help = (
        "Expires memberships whose end date has passed and sends "
        "'expiring soon' notifications to clients whose membership is "
        "about to lapse. Intended to be run once a day via cron / a "
        "scheduled task."
    )

    def handle(self, *args, **options):
        result = sync_membership_statuses()

        self.stdout.write(
            self.style.SUCCESS(
                f"Expired {result['expired_count']} membership(s). "
                f"Sent {result['notified_count']} expiring-soon "
                f"notification(s)."
            )
        )
