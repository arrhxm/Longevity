import datetime

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from clients.models import ClientProfile
from notifications.models import Notification

from .models import Appointment
from .services import find_conflicting_appointment


class AppointmentConflictTests(TestCase):

    def setUp(self):
        self.dietitian = User.objects.create_user(
            username="dietitian3", password="pass12345", role="DIETITIAN",
        )

        self.client_a_user = User.objects.create_user(
            username="client_a", password="pass12345", role="CLIENT",
        )
        self.profile_a = ClientProfile.objects.create(
            user=self.client_a_user
        )

        self.client_b_user = User.objects.create_user(
            username="client_b", password="pass12345", role="CLIENT",
        )
        self.profile_b = ClientProfile.objects.create(
            user=self.client_b_user
        )

        self.existing = Appointment.objects.create(
            client=self.profile_a,
            date=datetime.date(2026, 10, 1),
            time=datetime.time(10, 0),
            duration_minutes=30,
            status=Appointment.Status.SCHEDULED,
        )

    def test_overlapping_slot_is_detected(self):
        conflict = find_conflicting_appointment(
            datetime.date(2026, 10, 1),
            datetime.time(10, 15),
            30,
        )
        self.assertEqual(conflict, self.existing)

    def test_non_overlapping_slot_has_no_conflict(self):
        conflict = find_conflicting_appointment(
            datetime.date(2026, 10, 1),
            datetime.time(11, 0),
            30,
        )
        self.assertIsNone(conflict)

    def test_cancelled_appointment_does_not_block_the_slot(self):
        self.existing.status = Appointment.Status.CANCELLED
        self.existing.save()

        conflict = find_conflicting_appointment(
            datetime.date(2026, 10, 1),
            datetime.time(10, 0),
            30,
        )
        self.assertIsNone(conflict)

    def test_create_appointment_view_rejects_conflict(self):
        self.client.login(username="dietitian3", password="pass12345")

        response = self.client.post(
            reverse("create_appointment", args=[self.client_b_user.id]),
            {
                "date": "2026-10-01",
                "time": "10:15",
                "duration_minutes": 30,
                "status": "SCHEDULED",
                "reason": "",
                "notes": "",
            },
        )

        # Should re-render the form with an error, not redirect.
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Appointment.objects.filter(client=self.profile_b).exists()
        )


class AppointmentStatusNotificationTests(TestCase):

    def setUp(self):
        self.dietitian = User.objects.create_user(
            username="dietitian4", password="pass12345", role="DIETITIAN",
        )
        self.client_user = User.objects.create_user(
            username="client_c", password="pass12345", role="CLIENT",
        )
        self.profile = ClientProfile.objects.create(user=self.client_user)

        self.appointment = Appointment.objects.create(
            client=self.profile,
            date=datetime.date(2026, 10, 5),
            time=datetime.time(9, 0),
            duration_minutes=30,
            status=Appointment.Status.SCHEDULED,
        )

        self.client.login(username="dietitian4", password="pass12345")

    def test_cancelling_notifies_client(self):
        self.client.post(
            reverse(
                "update_appointment_status", args=[self.appointment.id]
            ),
            {"status": "CANCELLED", "next": "/"},
        )

        self.appointment.refresh_from_db()
        self.assertEqual(
            self.appointment.status, Appointment.Status.CANCELLED
        )

        self.assertTrue(
            Notification.objects.filter(
                user=self.client_user,
                title="Appointment Cancelled",
            ).exists()
        )

    def test_completing_notifies_client(self):
        self.client.post(
            reverse(
                "update_appointment_status", args=[self.appointment.id]
            ),
            {"status": "COMPLETED", "next": "/"},
        )

        self.appointment.refresh_from_db()
        self.assertEqual(
            self.appointment.status, Appointment.Status.COMPLETED
        )

        self.assertTrue(
            Notification.objects.filter(
                user=self.client_user,
                title="Appointment Completed",
            ).exists()
        )
