import datetime

from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from clients.models import ClientProfile
from notifications.models import Notification

from .models import Membership
from .services import sync_membership_statuses


class MembershipSyncTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="client_sync", password="pass12345", role="CLIENT",
        )
        self.profile = ClientProfile.objects.create(user=self.user)
        self.today = timezone.localdate()

    def test_overdue_active_membership_is_expired(self):
        membership = Membership.objects.create(
            client=self.profile,
            name="Old Plan",
            start_date=self.today - datetime.timedelta(days=100),
            end_date=self.today - datetime.timedelta(days=5),
            amount=200,
            status=Membership.Status.ACTIVE,
        )

        sync_membership_statuses()

        membership.refresh_from_db()
        self.assertEqual(membership.status, Membership.Status.EXPIRED)

    def test_membership_expiring_soon_gets_one_notification(self):
        Membership.objects.create(
            client=self.profile,
            name="Expiring Plan",
            start_date=self.today - datetime.timedelta(days=60),
            end_date=self.today + datetime.timedelta(days=3),
            amount=300,
            status=Membership.Status.ACTIVE,
        )

        sync_membership_statuses()
        sync_membership_statuses()  # run twice on purpose

        notifications = Notification.objects.filter(
            user=self.user,
            notification_type=Notification.NotificationType.PAYMENT_DUE,
        )
        self.assertEqual(notifications.count(), 1)

    def test_membership_not_expiring_soon_gets_no_notification(self):
        Membership.objects.create(
            client=self.profile,
            name="Fresh Plan",
            start_date=self.today,
            end_date=self.today + datetime.timedelta(days=90),
            amount=300,
            status=Membership.Status.ACTIVE,
        )

        sync_membership_statuses()

        notifications = Notification.objects.filter(
            user=self.user,
            notification_type=Notification.NotificationType.PAYMENT_DUE,
        )
        self.assertEqual(notifications.count(), 0)
