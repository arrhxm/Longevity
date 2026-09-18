import calendar
import uuid
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from notifications.models import Notification
from payments.models import Membership, MembershipPlan, Payment

from .forms import EnrollmentProfileForm
from .models import ClientProfile, Enrollment


def _add_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _client_profile(request):
    profile, _ = ClientProfile.objects.get_or_create(user=request.user)
    if not profile.phone and request.user.phone:
        profile.phone = request.user.phone
        profile.save(update_fields=["phone", "updated_at"])
    return profile


def _require_client(request):
    return request.user.is_authenticated and request.user.role == "CLIENT"


@login_required
def renew_membership_plan(request):
    if not _require_client(request):
        return redirect("dashboard")

    profile = _client_profile(request)
    from payments.services import sync_membership_statuses
    sync_membership_statuses()

    memberships = profile.memberships.all().order_by("-start_date")
    if not memberships.exists():
        return redirect("enrollment_profile")

    current_membership = (
        profile.memberships.filter(status=Membership.Status.ACTIVE)
        .order_by("-end_date")
        .first()
    )
    if current_membership:
        today = timezone.localdate()
        days_remaining = (current_membership.end_date - today).days
        if days_remaining > 7:
            return redirect("client_dashboard")

    plans = MembershipPlan.objects.filter(country=profile.country, is_active=True)

    if request.method == "POST":
        plan_id = request.POST.get("plan")
        plan = get_object_or_404(plans, id=plan_id)
        request.session["renewal_plan_id"] = plan.id
        return redirect("renewal_payment")

    return render(request, "clients/renewal_plan.html", {
        "profile": profile,
        "plans": plans,
    })


@login_required
def renewal_payment(request):
    if not _require_client(request):
        return redirect("dashboard")

    profile = _client_profile(request)
    from payments.services import sync_membership_statuses
    sync_membership_statuses()

    plan_id = request.session.get("renewal_plan_id")
    plans = MembershipPlan.objects.filter(country=profile.country, is_active=True)
    plan = get_object_or_404(plans, id=plan_id) if plan_id else None
    if not plan:
        return redirect("renew_membership_plan")

    current_membership = (
        profile.memberships.filter(status=Membership.Status.ACTIVE)
        .order_by("-end_date")
        .first()
    )

    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "UPI")
        allowed_methods = {choice[0] for choice in Payment.PaymentMethod.choices}
        if payment_method not in allowed_methods:
            payment_method = "UPI"

        with transaction.atomic():
            today = timezone.localdate()
            if current_membership and current_membership.end_date >= today:
                start_date = current_membership.end_date + timedelta(days=1)
            else:
                start_date = today
            end_date = _add_months(start_date, plan.duration_months) - timedelta(days=1)

            membership = Membership.objects.create(
                client=profile,
                enrollment=None,
                name=plan.name,
                start_date=start_date,
                end_date=end_date,
                amount=plan.amount,
                status=Membership.Status.ACTIVE,
                notes=f"Membership renewal through Longevity+. Plan: {plan.name}.",
            )

            Payment.objects.create(
                membership=membership,
                amount=plan.amount,
                payment_date=today,
                payment_method=payment_method,
                status=Payment.Status.PAID,
                transaction_id=f"LP-RN-{uuid.uuid4().hex[:10].upper()}",
                notes="Renewal payment recorded through the development checkout.",
            )

            Notification.objects.create(
                user=request.user,
                notification_type=Notification.NotificationType.PAYMENT_RECEIVED,
                title="Membership Renewed",
                message=f"Your {plan.name} membership has been renewed. It is active from {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}.",
            )

        request.session.pop("renewal_plan_id", None)
        return redirect("client_dashboard")

    return render(request, "clients/renewal_payment.html", {
        "profile": profile,
        "plan": plan,
        "current_membership": current_membership,
    })


@login_required
def enrollment_profile(request):
    if not _require_client(request):
        return redirect("dashboard")

    profile = _client_profile(request)
    enrollment, _ = Enrollment.objects.get_or_create(client=profile)

    if enrollment.status == Enrollment.Status.COMPLETED:
        return redirect("client_dashboard")

    if request.method == "POST":
        form = EnrollmentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            enrollment.status = Enrollment.Status.PROFILE_COMPLETE
            enrollment.save(update_fields=["status", "updated_at"])
            return redirect("enrollment_plan")
    else:
        form = EnrollmentProfileForm(instance=profile)

    return render(
        request,
        "clients/enrollment_profile.html",
        {"form": form, "profile": profile, "enrollment": enrollment},
    )


@login_required
def enrollment_plan(request):
    if not _require_client(request):
        return redirect("dashboard")

    profile = _client_profile(request)
    enrollment, _ = Enrollment.objects.get_or_create(client=profile)

    if enrollment.status == Enrollment.Status.COMPLETED:
        return redirect("client_dashboard")

    if not profile.date_of_birth or not profile.gender or not profile.health_goal:
        return redirect("enrollment_profile")

    plans = MembershipPlan.objects.filter(country=profile.country, is_active=True)

    if request.method == "POST":
        plan_id = request.POST.get("plan")
        plan = get_object_or_404(plans, id=plan_id)
        enrollment.membership_plan = plan
        enrollment.status = Enrollment.Status.PENDING_PAYMENT
        enrollment.save(update_fields=["membership_plan", "status", "updated_at"])
        return redirect("enrollment_payment")

    return render(
        request,
        "clients/enrollment_plan.html",
        {"profile": profile, "plans": plans, "enrollment": enrollment},
    )


@login_required
def enrollment_payment(request):
    if not _require_client(request):
        return redirect("dashboard")

    profile = _client_profile(request)
    enrollment = get_object_or_404(
        Enrollment.objects.select_related("membership_plan"), client=profile
    )

    if enrollment.status == Enrollment.Status.COMPLETED:
        return redirect("client_dashboard")

    if not enrollment.membership_plan:
        return redirect("enrollment_plan")

    plan = enrollment.membership_plan

    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "UPI")
        allowed_methods = {choice[0] for choice in Payment.PaymentMethod.choices}
        if payment_method not in allowed_methods:
            payment_method = "UPI"

        with transaction.atomic():
            today = timezone.localdate()
            end_date = _add_months(today, plan.duration_months) - timedelta(days=1)

            membership = Membership.objects.filter(enrollment=enrollment).first()
            if membership is None:
                membership = Membership.objects.create(
                    client=profile,
                    enrollment=enrollment,
                    name=plan.name,
                    start_date=today,
                    end_date=end_date,
                    amount=plan.amount,
                    status=Membership.Status.ACTIVE,
                    notes=f"Enrolled through Longevity+ enrollment. Goal: {profile.get_health_goal_display()}.",
                )

            if not membership.payments.filter(status=Payment.Status.PAID).exists():
                Payment.objects.create(
                    membership=membership,
                    amount=plan.amount,
                    payment_date=today,
                    payment_method=payment_method,
                    status=Payment.Status.PAID,
                    transaction_id=f"LP-{uuid.uuid4().hex[:12].upper()}",
                    notes="Enrollment payment recorded through the development checkout.",
                )

            enrollment.status = Enrollment.Status.COMPLETED
            enrollment.enrolled_at = timezone.now()
            enrollment.save(update_fields=["status", "enrolled_at", "updated_at"])

            Notification.objects.create(
                user=request.user,
                notification_type=Notification.NotificationType.PAYMENT_RECEIVED,
                title="Enrollment Successful",
                message=f"Your {plan.name} membership is now active. Complete your initial measurements to get started.",
            )

        return redirect("initial_measurements")

    return render(
        request,
        "clients/enrollment_payment.html",
        {"profile": profile, "plan": plan, "enrollment": enrollment},
    )
