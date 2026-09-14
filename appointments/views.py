from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Appointment
from clients.models import ClientProfile
from .forms import AppointmentForm
from notifications.models import Notification

@login_required
def client_appointments(request):
    if request.user.role != "CLIENT":
        return redirect("dashboard")

    appointments = (
        Appointment.objects
        .filter(client=request.user.client_profile)
        .order_by("-date", "-time")
    )

    return render(
        request,
        "appointments/client_appointments.html",
        {
            "appointments": appointments,
        },
    )

@login_required
def create_appointment(request, client_id):
    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    client = ClientProfile.objects.get(user_id=client_id)

    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = client
            appointment.save()

            Notification.objects.create(
                user=client.user,
                notification_type=Notification.NotificationType.APPOINTMENT,
                title="New Appointment Scheduled",
                message=(
                    f"Your appointment has been scheduled for "
                    f"{appointment.date} at {appointment.time}."
                ),
            )

            return redirect("dietitian_dashboard")

    else:
        form = AppointmentForm()

    return render(
        request,
        "appointments/create_appointment.html",
        {
            "form": form,
            "client": client,
        },
    )