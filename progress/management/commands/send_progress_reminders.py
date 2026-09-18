from django.core.management.base import BaseCommand

from progress.services import send_progress_reminders


class Command(BaseCommand):
    help = "Create weekly weight and 30-day body measurement reminders for clients."

    def handle(self, *args, **options):
        send_progress_reminders()
        self.stdout.write(self.style.SUCCESS("Progress reminders checked."))
