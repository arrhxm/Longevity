from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Appointment
from clients.models import ClientProfile
from .forms import AppointmentForm
from .services import find_conflicting_appointment
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

    client, _ = ClientProfile.objects.get_or_create(user_id=client_id)

    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            conflict = find_conflicting_appointment(
                form.cleaned_data["date"],
                form.cleaned_data["time"],
                form.cleaned_data["duration_minutes"],
            )

            if conflict:
                form.add_error(
                    None,
                    "This overlaps with an existing appointment for "
                    f"{conflict.client.user.get_full_name() or conflict.client.user.username} "
                    f"at {conflict.time.strftime('%I:%M %p')} on "
                    f"{conflict.date}. Please choose a different time.",
                )
            else:
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


@login_required
def dietitian_appointments(request):
    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    today = timezone.localdate()

    upcoming_appointments = (
        Appointment.objects
        .filter(
            status=Appointment.Status.SCHEDULED,
            date__gte=today,
        )
        .select_related("client__user")
        .order_by("date", "time")
    )

    overdue_appointments = (
        Appointment.objects
        .filter(
            status=Appointment.Status.SCHEDULED,
            date__lt=today,
        )
        .select_related("client__user")
        .order_by("-date", "-time")
    )

    past_appointments_qs = (
        Appointment.objects
        .exclude(status=Appointment.Status.SCHEDULED)
        .select_related("client__user")
        .order_by("-date", "-time")
    )

    paginator = Paginator(past_appointments_qs, 15)
    page_number = request.GET.get("page")
    past_appointments = paginator.get_page(page_number)

    return render(
        request,
        "appointments/dietitian_appointments.html",
        {
            "upcoming_appointments": upcoming_appointments,
            "overdue_appointments": overdue_appointments,
            "past_appointments": past_appointments,
        },
    )


@login_required
def edit_appointment(request, appointment_id):
    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    original_status = appointment.status
    original_date = appointment.date
    original_time = appointment.time

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)

        if form.is_valid():
            conflict = None

            if form.cleaned_data["status"] == Appointment.Status.SCHEDULED:
                conflict = find_conflicting_appointment(
                    form.cleaned_data["date"],
                    form.cleaned_data["time"],
                    form.cleaned_data["duration_minutes"],
                    exclude_id=appointment.id,
                )

            if conflict:
                form.add_error(
                    None,
                    "This overlaps with an existing appointment for "
                    f"{conflict.client.user.get_full_name() or conflict.client.user.username} "
                    f"at {conflict.time.strftime('%I:%M %p')} on "
                    f"{conflict.date}. Please choose a different time.",
                )
            else:
                updated = form.save()

                _notify_appointment_change(
                    updated,
                    original_status,
                    original_date,
                    original_time,
                )

                return redirect("dietitian_appointments")

    else:
        form = AppointmentForm(instance=appointment)

    return render(
        request,
        "appointments/edit_appointment.html",
        {
            "form": form,
            "appointment": appointment,
            "client": appointment.client,
        },
    )


@login_required
def update_appointment_status(request, appointment_id):
    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        new_status = request.POST.get("status")

        if new_status in Appointment.Status.values:
            original_status = appointment.status
            appointment.status = new_status
            appointment.save()

            _notify_appointment_change(
                appointment,
                original_status,
                appointment.date,
                appointment.time,
            )

    next_url = request.POST.get("next") or "dietitian_appointments"
    return redirect(next_url)


def _notify_appointment_change(
    appointment,
    original_status,
    original_date,
    original_time,
):
    """
    Fires the right client-facing notification after an appointment is
    edited or has its status changed.
    """
    status_changed = appointment.status != original_status
    rescheduled = (
        appointment.date != original_date
        or appointment.time != original_time
    )

    if status_changed and appointment.status == Appointment.Status.CANCELLED:
        Notification.objects.create(
            user=appointment.client.user,
            notification_type=Notification.NotificationType.APPOINTMENT,
            title="Appointment Cancelled",
            message=(
                f"Your appointment on {appointment.date} at "
                f"{appointment.time} has been cancelled."
            ),
        )
    elif status_changed and appointment.status == Appointment.Status.COMPLETED:
        Notification.objects.create(
            user=appointment.client.user,
            notification_type=Notification.NotificationType.APPOINTMENT,
            title="Appointment Completed",
            message=(
                f"Your appointment on {appointment.date} has been "
                f"marked as completed."
            ),
        )
    elif status_changed and appointment.status == Appointment.Status.NO_SHOW:
        Notification.objects.create(
            user=appointment.client.user,
            notification_type=Notification.NotificationType.APPOINTMENT,
            title="Appointment Missed",
            message=(
                f"You were marked as a no-show for your appointment on "
                f"{appointment.date} at {appointment.time}. Please "
                f"reach out to reschedule."
            ),
        )
    elif rescheduled:
        Notification.objects.create(
            user=appointment.client.user,
            notification_type=Notification.NotificationType.APPOINTMENT,
            title="Appointment Rescheduled",
            message=(
                f"Your appointment has been rescheduled to "
                f"{appointment.date} at {appointment.time}."
            ),
        )