from django.core.management.base import BaseCommand

from appointments.services import send_appointment_reminders


class Command(BaseCommand):
    help = (
        "Sends a reminder notification to clients with a SCHEDULED "
        "appointment tomorrow. Intended to be run once a day via cron / "
        "a scheduled task."
    )

    def handle(self, *args, **options):
        result = send_appointment_reminders()

        self.stdout.write(
            self.style.SUCCESS(
                f"Sent {result['reminded_count']} appointment "
                f"reminder(s)."
            )
        )
