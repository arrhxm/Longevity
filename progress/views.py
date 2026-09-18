from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from clients.models import ClientProfile, Enrollment
from .forms import InitialMeasurementForm, MonthlyMeasurementForm, ProgressPhotoForm, ProgressPhotoSetForm, ProgressRecordForm, WeeklyWeightForm
from .models import ProgressPhotoSet, ProgressRecord
from notifications.models import Notification


def _active_member(profile):
    return profile.memberships.filter(
        status="ACTIVE"
    ).order_by("-start_date").first()


def _save_progress(profile, form, record_type):
    data = form.cleaned_data.copy()
    if record_type == ProgressRecord.RecordType.WEEKLY_WEIGHT:
        data.pop("front_photo", None)
        data.pop("side_photo", None)
        data.pop("back_photo", None)
    record = ProgressRecord.objects.create(
        client=profile,
        date=timezone.localdate(),
        record_type=record_type,
        **data,
    )
    if record.weight is not None:
        profile.current_weight = record.weight
        profile.save(update_fields=["current_weight", "updated_at"])
    return record


@login_required
def initial_measurements(request):
    if request.user.role != "CLIENT":
        return redirect("dashboard")

    profile = get_object_or_404(ClientProfile, user=request.user)
    enrollment = getattr(profile, "enrollment", None)
    membership = _active_member(profile)

    if not enrollment or enrollment.status != Enrollment.Status.COMPLETED or not membership:
        return redirect("enrollment_profile")

    if profile.height and profile.progress_records.filter(record_type=ProgressRecord.RecordType.INITIAL).exists():
        return redirect("client_dashboard")

    if request.method == "POST":
        form = InitialMeasurementForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            height = data.pop("height")
            weight = data.pop("weight")
            notes = data.pop("notes", "")
            profile.height = height
            profile.current_weight = weight
            profile.save(update_fields=["height", "current_weight", "updated_at"])
            ProgressRecord.objects.create(
                client=profile,
                date=timezone.localdate(),
                record_type=ProgressRecord.RecordType.INITIAL,
                weight=weight,
                notes=notes,
                **data,
            )
            Notification.objects.create(
                user=request.user,
                notification_type=Notification.NotificationType.PROGRESS,
                title="Initial Measurements Saved",
                message="Your initial measurements have been saved. Your dietitian can now use your profile to prepare your diet plan.",
            )
            return redirect("client_dashboard")
    else:
        form = InitialMeasurementForm()

    return render(request, "progress/initial_measurements.html", {"form": form, "profile": profile})


@login_required
def weekly_weight_update(request):
    if request.user.role != "CLIENT":
        return redirect("dashboard")
    profile = get_object_or_404(ClientProfile, user=request.user)
    if not _active_member(profile):
        return redirect("enrollment_profile")

    if request.method == "POST":
        form = WeeklyWeightForm(request.POST)
        if form.is_valid():
            _save_progress(profile, form, ProgressRecord.RecordType.WEEKLY_WEIGHT)
            return redirect("client_progress")
    else:
        form = WeeklyWeightForm()
    return render(request, "progress/weekly_weight.html", {"form": form, "profile": profile})


@login_required
def monthly_measurement_update(request):
    if request.user.role != "CLIENT":
        return redirect("dashboard")
    profile = get_object_or_404(ClientProfile, user=request.user)
    if not _active_member(profile):
        return redirect("enrollment_profile")

    if request.method == "POST":
        form = MonthlyMeasurementForm(request.POST)
        if form.is_valid():
            _save_progress(profile, form, ProgressRecord.RecordType.MONTHLY_MEASUREMENT)
            return redirect("client_progress")
    else:
        form = MonthlyMeasurementForm()
    return render(request, "progress/monthly_measurements.html", {"form": form, "profile": profile})


@login_required
def progress_photos(request):
    if request.user.role != "CLIENT":
        return redirect("dashboard")

    profile = get_object_or_404(ClientProfile, user=request.user)
    if profile.gender != ClientProfile.Gender.MALE:
        return redirect("client_progress")
    if not _active_member(profile):
        return redirect("enrollment_profile")

    if request.method == "POST":
        form = ProgressPhotoSetForm(request.POST, request.FILES)
        if form.is_valid():
            photo_set = form.save(commit=False)
            photo_set.client = profile
            photo_set.save()
            return redirect("client_progress")
    else:
        form = ProgressPhotoSetForm()

    photo_sets = profile.progress_photo_sets.all()
    return render(request, "progress/progress_photos.html", {
        "form": form,
        "profile": profile,
        "photo_sets": photo_sets,
    })


@login_required
def add_progress(request, client_id):
    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    client = get_object_or_404(ClientProfile, user_id=client_id)

    if request.method == "POST":
        form = ProgressRecordForm(request.POST)
        if form.is_valid():
            progress = form.save(commit=False)
            progress.client = client
            progress.save()
            if progress.weight is not None:
                client.current_weight = progress.weight
                client.save(update_fields=["current_weight", "updated_at"])
            Notification.objects.create(
                user=client.user,
                notification_type=Notification.NotificationType.PROGRESS,
                title="New Progress Update",
                message=f"Your dietitian logged a new progress record for {progress.date}.",
            )
            return redirect("client_details", client_id=client.user_id)
    else:
        form = ProgressRecordForm(initial={"date": timezone.localdate()})

    return render(request, "accounts/add_progress.html", {"form": form, "client": client})


@login_required
def client_progress(request):
    if request.user.role != "CLIENT":
        return redirect("dashboard")

    profile = get_object_or_404(ClientProfile, user=request.user)
    progress_records = profile.progress_records.order_by("date", "created_at")

    chart_records = progress_records.exclude(weight__isnull=True)
    chart_labels = [record.date.strftime("%d %b") for record in chart_records]
    chart_weights = [float(record.weight) for record in chart_records]

    return render(
        request,
        "accounts/client_progress.html",
        {
            "profile": profile,
            "progress_records": progress_records,
            "chart_labels": chart_labels,
            "chart_weights": chart_weights,
        },
    )
