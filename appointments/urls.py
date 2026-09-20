from django.urls import path
from . import views
from .views import (
    client_appointments,
    create_appointment,
    dietitian_appointments,
    edit_appointment,
    update_appointment_status,
    request_reschedule,
    handle_reschedule_request,
    choose_reschedule_time,
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
        "<int:appointment_id>/reschedule/",
        request_reschedule,
        name="request_reschedule",
    ),
    path(
        "reschedule-request/<int:request_id>/handle/",
        handle_reschedule_request,
        name="handle_reschedule_request",
    ),
    path(
        "reschedule-request/<int:request_id>/choose/",
        choose_reschedule_time,
        name="choose_reschedule_time",
    ),
    path(
        "<int:appointment_id>/status/",
        views.update_appointment_status,
        name="update_appointment_status",
    ),
]
