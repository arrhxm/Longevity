from django.urls import path

from .views import (
    login_view,
    logout_view,
    dashboard,
    admin_dashboard,
    dietitian_dashboard,
    client_dashboard,
    client_profile,
    dietitian_client_progress,
    client_progress,
    add_payment,
    client_memberships,
    client_memberships_view,
    revenue_report,
    request_otp,
    verify_otp,
    complete_registration,
    client_details,
    edit_client_profile,
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),

    path(
        "admin-dashboard/",
        admin_dashboard,
        name="admin_dashboard",
    ),

    path(
        "dietitian-dashboard/",
        dietitian_dashboard,
        name="dietitian_dashboard",
    ),

    path(
        "client-dashboard/",
        client_dashboard,
        name="client_dashboard",
    ),
    path(
        "profile/",
        client_profile,
        name="client_profile",
    ),
    path(
        "dietitian/client/<int:client_id>/progress/",
        dietitian_client_progress,
        name="dietitian_client_progress",
    ),
    path(
        "progress/",
        client_progress,
        name="client_progress",
    ),
    path(
        "dietitian/membership/<int:membership_id>/payment/add/",
        add_payment,
        name="add_payment",
    ),
    path(
        "dietitian/client/<int:client_id>/memberships/",
        client_memberships,
        name="client_memberships",
    ),
    path(
        "my-memberships/",
        client_memberships_view,
        name="client_memberships_view",
    ),
    path(
        "dietitian/revenue/",
        revenue_report,
        name="revenue_report",
    ),
    path(
        "register/",
        request_otp,
        name="register",
    ),

    path(
        "verify-otp/",
        verify_otp,
        name="verify_otp",
    ),

    path(
        "complete-registration/",
        complete_registration,
        name="complete_registration",
    ),
    path(
        "dietitian/client/<int:client_id>/",
        client_details,
        name="client_details",
    ),
    path(
        "dietitian/client/<int:client_id>/edit/",
        edit_client_profile,
        name="edit_client_profile",
    ),
]