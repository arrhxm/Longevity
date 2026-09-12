from django.urls import path

from .views import (
    admin_dashboard,
    add_meal,
    add_payment,
    add_progress,
    client_dashboard,
    client_profile,
    client_progress,
    create_diet_plan,
    create_membership,
    dashboard,
    dietitian_dashboard,
    login_view,
    logout_view,
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
        "dietitian/diet-plan/create/<int:client_id>/",
        create_diet_plan,
        name="create_diet_plan",
    ),
    path(
        "dietitian/diet-plan/<int:diet_plan_id>/add-meal/",
         add_meal,
        name="add_meal",
    ),
    path(
        "dietitian/client/<int:client_id>/progress/add/",
        add_progress,
        name="add_progress",
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
]