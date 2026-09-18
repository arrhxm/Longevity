import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from payments.models import Membership, MembershipPlan, Payment
from progress.models import ProgressRecord


class EnrollmentFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="enroll_client",
            password="pass12345",
            first_name="Enroll",
            last_name="Client",
            email="enroll@example.com",
            phone="9999999999",
            role=User.Role.CLIENT,
        )
        self.client.login(username="enroll_client", password="pass12345")

    def test_india_plans_have_required_prices(self):
        expected = {3: 7999, 6: 14999, 9: 16999, 12: 19999}
        self.assertEqual(
            dict(MembershipPlan.objects.filter(country="IN").values_list("duration_months", "amount")),
            {months: amount for months, amount in expected.items()},
        )

    def test_successful_enrollment_creates_membership_and_payment(self):
        response = self.client.post(
            reverse("enrollment_profile"),
            {
                "date_of_birth": "2003-01-15",
                "gender": "MALE",
                "country": "IN",
                "state": "Madhya Pradesh",
                "city": "Bhopal",
                "health_goal": "FAT_LOSS",
            },
        )
        self.assertRedirects(response, reverse("enrollment_plan"))

        plan = MembershipPlan.objects.get(duration_months=6, country="IN")
        response = self.client.post(
            reverse("enrollment_plan"),
            {"plan": plan.id},
        )
        self.assertRedirects(response, reverse("enrollment_payment"))

        response = self.client.post(
            reverse("enrollment_payment"),
            {"payment_method": "UPI"},
        )
        self.assertRedirects(response, reverse("initial_measurements"))

        membership = Membership.objects.get(client__user=self.user)
        self.assertEqual(membership.amount, plan.amount)
        self.assertEqual(membership.status, Membership.Status.ACTIVE)
        self.assertEqual(membership.enrollment.membership_plan_id, plan.id)
        payment = Payment.objects.get(membership=membership)
        self.assertEqual(payment.status, Payment.Status.PAID)
        self.assertEqual(payment.amount, plan.amount)

    def test_initial_measurements_use_exact_fields(self):
        self.client.post(
            reverse("enrollment_profile"),
            {
                "date_of_birth": "2003-01-15",
                "gender": "MALE",
                "country": "IN",
                "state": "Madhya Pradesh",
                "city": "Bhopal",
                "health_goal": "FAT_LOSS",
            },
        )
        plan = MembershipPlan.objects.get(duration_months=3, country="IN")
        self.client.post(reverse("enrollment_plan"), {"plan": plan.id})
        self.client.post(reverse("enrollment_payment"), {"payment_method": "UPI"})

        response = self.client.post(
            reverse("initial_measurements"),
            {
                "height": "175",
                "weight": "72",
                "neck_circumference": "15",
                "chest_circumference": "40",
                "shoulder_circumference": "18",
                "stomach_on_naval": "34",
                "stomach_above_naval": "33",
                "stomach_below_naval": "35",
                "arms_flexed": "14",
                "waist": "32",
                "thighs_mid_section": "22",
                "notes": "Initial baseline",
            },
        )
        self.assertRedirects(response, reverse("client_dashboard"))

        record = ProgressRecord.objects.get(client__user=self.user)
        self.assertEqual(record.record_type, ProgressRecord.RecordType.INITIAL)
        self.assertEqual(record.weight, 72)
        self.assertEqual(record.waist, 32)
        self.assertEqual(record.thighs_mid_section, 22)
