from django.urls import path
from .views import client_appointments, create_appointment

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
]