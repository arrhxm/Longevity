import datetime

from django.test import TestCase
from django.urls import reverse

from clients.models import ClientProfile

from .models import User


class LoginAndRoutingTests(TestCase):
    """
    Covers the login redirect bug: after logging in, each role must land
    on its own dashboard (not always on client_profile).
    """

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_test", password="pass12345", role="ADMIN",
        )
        self.dietitian = User.objects.create_user(
            username="dietitian_test", password="pass12345",
            role="DIETITIAN",
        )
        self.client_user = User.objects.create_user(
            username="client_test", password="pass12345", role="CLIENT",
        )

    def _login(self, username):
        return self.client.post(
            reverse("login"),
            {"identifier": username, "password": "pass12345"},
        )

    def test_admin_redirects_to_admin_dashboard(self):
        self._login("admin_test")
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("admin_dashboard"))

    def test_dietitian_redirects_to_dietitian_dashboard(self):
        self._login("dietitian_test")
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("dietitian_dashboard"))

    def test_client_redirects_to_client_dashboard(self):
        self._login("client_test")
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("client_dashboard"))

    def test_login_redirects_straight_to_dashboard(self):
        response = self._login("client_test")
        self.assertRedirects(
            response, reverse("dashboard"), fetch_redirect_response=False,
        )


class DietitianClientFlowTests(TestCase):
    """
    Covers the create_diet_plan 500-on-GET bug and the add_progress
    wrong-redirect-id bug.
    """

    def setUp(self):
        self.dietitian = User.objects.create_user(
            username="dietitian2", password="pass12345", role="DIETITIAN",
        )
        self.client_user = User.objects.create_user(
            username="client2", password="pass12345", role="CLIENT",
        )
        ClientProfile.objects.create(user=self.client_user)
        self.client.login(username="dietitian2", password="pass12345")

    def test_create_diet_plan_get_renders_form(self):
        response = self.client.get(
            reverse("create_diet_plan", args=[self.client_user.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_create_diet_plan_post_creates_plan(self):
        response = self.client.post(
            reverse("create_diet_plan", args=[self.client_user.id]),
            {
                "name": "Test Plan",
                "description": "desc",
                "start_date": "2026-01-01",
                "end_date": "2026-02-01",
                "calories_per_day": 1800,
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_add_progress_redirects_with_correct_user_id(self):
        response = self.client.post(
            reverse("add_progress", args=[self.client_user.id]),
            {
                "date": "2026-01-15",
                "weight": "70.5",
                "body_fat_percentage": "20",
                "waist": "80",
                "chest": "95",
                "hips": "90",
                "notes": "",
            },
        )
        # Must redirect back using the client's *user* id, not the
        # ClientProfile's own pk.
        self.assertRedirects(
            response,
            reverse("add_progress", args=[self.client_user.id]),
        )
