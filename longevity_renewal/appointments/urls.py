from django.urls import path
from .views import (
    client_appointments,
    create_appointment,
    dietitian_appointments,
    edit_appointment,
    update_appointment_status,
)

urlpatterns = [
    path(
        "my-appointments/",
        client_appointments,
        name="client_appointments",
    ),

    path(
        "create/<int:client_id>/",
        create_appointment,
        name="create_appointment",
    ),

    path(
        "manage/",
        dietitian_appointments,
        name="dietitian_appointments",
    ),

    path(
        "<int:appointment_id>/edit/",
        edit_appointment,
        name="edit_appointment",
    ),

    path(
        "<int:appointment_id>/status/",
        update_appointment_status,
        name="update_appointment_status",
    ),
]
