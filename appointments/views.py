from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Appointment, RescheduleRequest
from clients.models import ClientProfile
from .forms import AppointmentForm
from .services import find_conflicting_appointment
from notifications.models import Notification
from payments.models import Membership

@login_required
def client_appointments(request):
    if request.user.role != "CLIENT":
        return redirect("dashboard")

    client = request.user.client_profile
    from payments.services import sync_membership_statuses
    sync_membership_statuses()
    active_membership = client.memberships.filter(status=Membership.Status.ACTIVE).first()
    has_membership_history = client.memberships.exists()
    if not has_membership_history:
        return redirect("client_dashboard")

    appointments = list(
        Appointment.objects
        .filter(client=client)
        .prefetch_related("reschedule_requests")
        .order_by("date", "time")
    )
    today = timezone.localdate()
    for appointment in appointments:
        appointment.pending_reschedule = any(
            item.status == RescheduleRequest.Status.PENDING
            for item in appointment.reschedule_requests.all()
        )

    reschedule_history = RescheduleRequest.objects.filter(
        client=client,
    ).select_related("appointment").order_by("-created_at")

    return render(
        request,
        "appointments/client_appointments.html",
        {
            "appointments": appointments,
            "active_membership": active_membership,
            "today": today,
            "reschedule_history": reschedule_history,
        },
    )

@login_required
def create_appointment(request, client_id):
    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    client, _ = ClientProfile.objects.get_or_create(user_id=client_id)

    from payments.services import sync_membership_statuses
    sync_membership_statuses()
    if not Membership.objects.filter(client=client, status=Membership.Status.ACTIVE).exists():
        return redirect("client_details", client_id=client.user_id)

    today = timezone.localdate()

    upcoming_appointments = (
        Appointment.objects
        .filter(
            client=client,
            status=Appointment.Status.SCHEDULED,
            date__gte=today,
        )
        .order_by("date", "time")
    )

    past_appointments = (
        Appointment.objects
        .filter(client=client)
        .exclude(
            status=Appointment.Status.SCHEDULED,
            date__gte=today,
        )
        .order_by("-date", "-time")
    )

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

                return redirect(
                    "create_appointment",
                    client_id=client.user_id,
                )

    else:
        form = AppointmentForm()

    return render(
        request,
        "appointments/create_appointment.html",
        {
            "form": form,
            "client": client,
            "upcoming_appointments": upcoming_appointments,
            "past_appointments": past_appointments,
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

    reschedule_requests = RescheduleRequest.objects.filter(
        appointment__client__assigned_dietitian=request.user,
        status=RescheduleRequest.Status.PENDING,
    ).select_related("appointment", "client__user").order_by("created_at")

    return render(
        request,
        "appointments/dietitian_appointments.html",
        {
            "upcoming_appointments": upcoming_appointments,
            "overdue_appointments": overdue_appointments,
            "past_appointments": past_appointments,
            "reschedule_requests": reschedule_requests,
        },
    )


@login_required
def request_reschedule(request, appointment_id):
    if request.user.role != "CLIENT":
        return redirect("dashboard")
    appointment = get_object_or_404(
        Appointment.objects.select_related("client"),
        id=appointment_id,
        client__user=request.user,
    )
    from payments.services import sync_membership_statuses
    sync_membership_statuses()
    active_membership = appointment.client.memberships.filter(status=Membership.Status.ACTIVE).first()
    if not active_membership or appointment.status != Appointment.Status.SCHEDULED:
        return redirect("client_appointments")
    if appointment.date < timezone.localdate():
        return redirect("client_appointments")
    if request.method == "POST":
        requested_date = request.POST.get("requested_date")
        requested_time = request.POST.get("requested_time")
        reason = request.POST.get("reason", "").strip()
        try:
            from datetime import date as date_type, time as time_type
            new_date = date_type.fromisoformat(requested_date)
            new_time = time_type.fromisoformat(requested_time)
        except (TypeError, ValueError):
            return redirect("client_appointments")
        if new_date < timezone.localdate():
            return redirect("client_appointments")
        if RescheduleRequest.objects.filter(appointment=appointment, status=RescheduleRequest.Status.PENDING).exists():
            return redirect("client_appointments")
        conflict = find_conflicting_appointment(new_date, new_time, appointment.duration_minutes, exclude_id=appointment.id)
        if conflict:
            return redirect("client_appointments")
        request_obj = RescheduleRequest.objects.create(
            appointment=appointment,
            client=appointment.client,
            original_date=appointment.date,
            original_time=appointment.time,
            requested_date=new_date,
            requested_time=new_time,
            reason=reason,
        )
        if appointment.client.assigned_dietitian_id:
            Notification.objects.create(
                user=appointment.client.assigned_dietitian,
                notification_type=Notification.NotificationType.APPOINTMENT,
                title="Reschedule Request",
                message=f"{appointment.client} requested {new_date} at {new_time} for an appointment.",
            )
        return redirect("client_appointments")
    return redirect("client_appointments")


@login_required
def handle_reschedule_request(request, request_id):
    if request.user.role != "DIETITIAN":
        return redirect("dashboard")
    reschedule = get_object_or_404(RescheduleRequest.objects.select_related("appointment", "client__user"), id=request_id, appointment__client__assigned_dietitian=request.user)
    if request.method != "POST" or reschedule.status != RescheduleRequest.Status.PENDING:
        return redirect("dietitian_appointments")
    action = request.POST.get("action")
    if action == "accept":
        conflict = find_conflicting_appointment(
            reschedule.requested_date,
            reschedule.requested_time,
            reschedule.appointment.duration_minutes,
            exclude_id=reschedule.appointment_id,
        )
        if conflict:
            return redirect("dietitian_appointments")
        reschedule.appointment.date = reschedule.requested_date
        reschedule.appointment.time = reschedule.requested_time
        reschedule.appointment.reminder_sent = False
        reschedule.appointment.save(update_fields=["date", "time", "reminder_sent", "updated_at"])
        reschedule.status = RescheduleRequest.Status.APPROVED
        message = f"Your appointment has been rescheduled to {reschedule.requested_date} at {reschedule.requested_time}."
    elif action == "decline":
        reschedule.status = RescheduleRequest.Status.DECLINED
        message = "Your appointment reschedule request was declined."
    else:
        return redirect("dietitian_appointments")
    reschedule.handled_by = request.user
    reschedule.handled_at = timezone.now()
    reschedule.save(update_fields=["status", "handled_by", "handled_at"])
    Notification.objects.create(
        user=reschedule.client.user,
        notification_type=Notification.NotificationType.APPOINTMENT,
        title="Reschedule Request Update",
        message=message,
    )
    return redirect("dietitian_appointments")


@login_required
def choose_reschedule_time(request, request_id):
    if request.user.role != "DIETITIAN":
        return redirect("dashboard")
    reschedule = get_object_or_404(RescheduleRequest.objects.select_related("appointment", "client__user"), id=request_id, appointment__client__assigned_dietitian=request.user)
    if request.method == "POST" and reschedule.status == RescheduleRequest.Status.PENDING:
        try:
            from datetime import date as date_type, time as time_type
            new_date = date_type.fromisoformat(request.POST.get("date"))
            new_time = time_type.fromisoformat(request.POST.get("time"))
        except (TypeError, ValueError):
            return redirect("dietitian_appointments")
        conflict = find_conflicting_appointment(new_date, new_time, reschedule.appointment.duration_minutes, exclude_id=reschedule.appointment_id)
        if conflict:
            return redirect("dietitian_appointments")
        reschedule.appointment.date = new_date
        reschedule.appointment.time = new_time
        reschedule.appointment.reminder_sent = False
        reschedule.appointment.save(update_fields=["date", "time", "reminder_sent", "updated_at"])
        reschedule.status = RescheduleRequest.Status.APPROVED
        reschedule.handled_by = request.user
        reschedule.handled_at = timezone.now()
        reschedule.save(update_fields=["status", "handled_by", "handled_at"])
        Notification.objects.create(
            user=reschedule.client.user,
            notification_type=Notification.NotificationType.APPOINTMENT,
            title="Appointment Rescheduled",
            message=f"Your appointment has been rescheduled to {new_date} at {new_time}.",
        )
    return redirect("dietitian_appointments")


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