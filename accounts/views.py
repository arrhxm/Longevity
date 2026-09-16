from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import redirect, render
from clients.models import ClientProfile
from nutrition.models import DietPlan, Meal
from nutrition.forms import DietPlanForm, MealForm
from progress.forms import ProgressRecordForm
from progress.models import ProgressRecord
from payments.forms import MembershipForm, PaymentForm
from payments.models import Membership, Payment
from decimal import Decimal
from django.shortcuts import get_object_or_404 
import random
from .models import User, RegistrationOTP
from .forms import OTPRequestForm, CompleteRegistrationForm,ClientProfileForm
from appointments.models import Appointment
from notifications.models import Notification

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=identifier,
            password=password,
        )

        # If username login failed, try email
        if user is None:
            from accounts.models import User

            try:
                user_obj = User.objects.get(email__iexact=identifier)
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password,
                )
            except User.DoesNotExist:
                pass

        # If email login failed, try phone
        if user is None:
            from accounts.models import User

            try:
                user_obj = User.objects.get(phone=identifier)
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password,
                )
            except User.DoesNotExist:
                pass

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        return render(
            request,
            "accounts/login.html",
            {
                "error": "Invalid username, email, phone number, or password."
            },
        )

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.is_superuser or request.user.role == "ADMIN":
        return redirect("admin_dashboard")

    if request.user.role == "DIETITIAN":
        return redirect("dietitian_dashboard")

    if request.user.role == "CLIENT":
        return redirect("client_dashboard")

    return redirect("logout")


def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if not (request.user.is_superuser or request.user.role == "ADMIN"):
        return redirect("dashboard")

    from accounts.models import User
    from payments.services import sync_membership_statuses

    sync_membership_statuses()


    client_count = User.objects.filter(role="CLIENT").count()
    dietitian_count = User.objects.filter(role="DIETITIAN").count()

    active_membership_count = Membership.objects.filter(
        status=Membership.Status.ACTIVE
    ).count()

    total_revenue = (
        Payment.objects
        .filter(status=Payment.Status.PAID)
        .aggregate(total=Sum("amount"))
        .get("total") or Decimal("0")
    )

    upcoming_appointment_count = Appointment.objects.filter(
        status=Appointment.Status.SCHEDULED
    ).count()

    active_diet_plan_count = DietPlan.objects.filter(
        is_active=True
    ).count()

    recent_clients = (
        User.objects
        .filter(role="CLIENT")
        .order_by("-date_joined")[:5]
    )

    upcoming_appointments = (
        Appointment.objects
        .filter(status=Appointment.Status.SCHEDULED)
        .select_related("client")
        .order_by("date", "time")[:5]
    )

    return render(
        request,
        "accounts/admin_dashboard.html",
        {
            "client_count": client_count,
            "dietitian_count": dietitian_count,
            "active_membership_count": active_membership_count,
            "total_revenue": total_revenue,
            "upcoming_appointment_count": upcoming_appointment_count,
            "active_diet_plan_count": active_diet_plan_count,
            "recent_clients": recent_clients,
            "upcoming_appointments": upcoming_appointments,
        },
    )


def dietitian_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    from accounts.models import User
    from payments.services import sync_membership_statuses

    sync_membership_statuses()

    clients_qs = (
        User.objects
        .filter(role="CLIENT")
        .prefetch_related(
            "client_profile__memberships"
        )
        .order_by("first_name", "last_name")
    )

    search_query = request.GET.get("q", "").strip()

    if search_query:
        clients_qs = clients_qs.filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    paginator = Paginator(clients_qs, 10)
    page_number = request.GET.get("page")
    clients = paginator.get_page(page_number)

    diet_plan_count = DietPlan.objects.filter(
        is_active=True).count()

    appointment_count = Appointment.objects.filter(
        status=Appointment.Status.SCHEDULED).count()

    return render(
        request,
        "accounts/dietitian_dashboard.html",
        {
            "clients": clients,
            "diet_plan_count": diet_plan_count,
            "appointment_count": appointment_count,
            "search_query": search_query,
        },
    )
def client_details(request, client_id):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    client = get_object_or_404(ClientProfile, user_id=client_id)

    diet_plans = (
        DietPlan.objects
        .filter(client=client.user)
        .prefetch_related("meals")
        .order_by("-start_date")
    )

    progress_records = (
        ProgressRecord.objects
        .filter(client=client)
        .order_by("-date")
    )

    memberships = (
        Membership.objects
        .filter(client=client)
        .order_by("-start_date")
    )

    appointments = (
        Appointment.objects
        .filter(client=client)
        .order_by("-date", "-time")
    )

    return render(
        request,
        "accounts/client_details.html",
        {
            "client": client,
            "diet_plans": diet_plans,
            "progress_records": progress_records,
            "memberships": memberships,
            "appointments": appointments,
        },
    )
def edit_client_profile(request, client_id):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    profile = get_object_or_404(ClientProfile, user_id=client_id)

    if request.method == "POST":
        form = ClientProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            return redirect("client_details", client_id=client_id)

    else:
        form = ClientProfileForm(instance=profile)

    return render(
        request,
        "accounts/edit_client_profile.html",
        {
            "form": form,
            "client": profile,
        },
    )


def client_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "CLIENT":
        return redirect("dashboard")

    profile, created = ClientProfile.objects.get_or_create(
        user=request.user
    )
    profile_complete = all([
    profile.date_of_birth,
    profile.height,
    profile.current_weight,
    profile.goal_weight,
    profile.health_goal,
    ])

    active_diet_plan = (
        DietPlan.objects
        .filter(
            client=request.user,
            is_active=True,
        )
        .prefetch_related("meals")
        .order_by("-start_date")
        .first()
    )
    active_membership = (
    Membership.objects
    .filter(
        client=profile,
        status=Membership.Status.ACTIVE,
    )
    .order_by("-start_date")
    .first()
    )

    next_appointment = (
    Appointment.objects
    .filter(
        client=profile,
        status=Appointment.Status.SCHEDULED,
    )
    .order_by("date", "time")
    .first()
    )
    notifications = (
        Notification.objects
        .filter(user=request.user)
        .order_by("-created_at")[:5]
    )

    return render(
        request,
        "accounts/client_dashboard.html",
        {
            "profile": profile,
            "active_diet_plan": active_diet_plan,
            "active_membership": active_membership,
            "next_appointment": next_appointment,
            "profile_complete": profile_complete,
            "notifications": notifications,
        },
    )
def client_profile(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "CLIENT":
        return redirect("dashboard")

    profile, created = ClientProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = ClientProfileForm(
            request.POST,
            instance=profile,
        )

        if form.is_valid():
            form.save()
            return redirect("client_profile")

    else:
        form = ClientProfileForm(instance=profile)

    return render(
        request,
        "accounts/client_profile.html",
        {
            "form": form,
            "profile": profile,
        },
    )
def create_diet_plan(request, client_id):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    client, _ = ClientProfile.objects.get_or_create(
        user_id=client_id
    )

    if request.method == "POST":
        form = DietPlanForm(request.POST)

        if form.is_valid():
            diet_plan = form.save(commit=False)
            diet_plan.client = client.user
            diet_plan.save()

            Notification.objects.create(
                user=client.user,
                notification_type=Notification.NotificationType.DIET_PLAN,
                title="New Diet Plan Assigned",
                message=f"Your dietitian has assigned you a new diet plan: {diet_plan.name}.",
            )

            return redirect(
                "add_meal", diet_plan_id=diet_plan.id,
            )
    else:
        form = DietPlanForm()

    return render(
        request,
        "accounts/create_diet_plan.html",
        {
            "form": form,
            "client": client,
        },
    )


def add_meal(request, diet_plan_id):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    diet_plan = DietPlan.objects.get(
        id=diet_plan_id
    )

    if request.method == "POST":
        form = MealForm(request.POST)

        if form.is_valid():
            meal = form.save(commit=False)
            meal.diet_plan = diet_plan
            meal.save()

            return redirect(
                "add_meal",
                diet_plan_id=diet_plan.id,
            )

    else:
        form = MealForm()

    return render(
        request,
        "accounts/add_meal.html",
        {
            "form": form,
            "diet_plan": diet_plan,
        },
    )
def add_progress(request, client_id):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    client, _ = ClientProfile.objects.get_or_create(
        user_id=client_id
    )

    if request.method == "POST":
        form = ProgressRecordForm(request.POST)

        if form.is_valid():
            progress = form.save(commit=False)
            progress.client = client
            progress.save()

            Notification.objects.create(
                user=client.user,
                notification_type=Notification.NotificationType.PROGRESS,
                title="New Progress Update",
                message=(
                    f"Your dietitian logged a new progress record for "
                    f"{progress.date}."
                ),
            )

            return redirect(
                "add_progress",
                client_id=client.user_id,
            )

    else:
        form = ProgressRecordForm()

    return render(
        request,
        "accounts/add_progress.html",
        {
            "form": form,
            "client": client,
        },
    )
def client_progress(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "CLIENT":
        return redirect("dashboard")

    profile, created = ClientProfile.objects.get_or_create(
        user=request.user
    )

    progress_records = (
        ProgressRecord.objects
        .filter(client=profile)
        .order_by("date")
    )

    chart_labels = [
        record.date.strftime("%d %b")
        for record in progress_records
        if record.weight is not None
    ]

    chart_weights = [
        float(record.weight)
        for record in progress_records
        if record.weight is not None
    ]

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
def create_membership(request, client_id):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    client, _ = ClientProfile.objects.get_or_create(
        user_id=client_id
    )

    if request.method == "POST":
        form = MembershipForm(request.POST)

        if form.is_valid():
            membership = form.save(commit=False)
            membership.client = client
            membership.save()

            return redirect(
                "dietitian_dashboard"
            )

    else:
        form = MembershipForm()

    return render(
        request,
        "accounts/create_membership.html",
        {
            "form": form,
            "client": client,
        },
    )
def add_payment(request, membership_id):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    membership = Membership.objects.get(
        id=membership_id
    )

    if request.method == "POST":
        form = PaymentForm(request.POST)

        if form.is_valid():
            payment = form.save(commit=False)
            payment.membership = membership
            payment.save()

            if payment.status == Payment.Status.PAID:
                title = "Payment Received"
                message = (
                    f"We've received your payment of ₹{payment.amount} "
                    f"for '{membership.name}'. Thank you!"
                )
            elif payment.status == Payment.Status.PARTIAL:
                title = "Partial Payment Received"
                message = (
                    f"We've received a partial payment of "
                    f"₹{payment.amount} for '{membership.name}'. "
                    f"A balance is still due."
                )
            else:
                title = "Payment Recorded"
                message = (
                    f"A payment of ₹{payment.amount} for "
                    f"'{membership.name}' has been recorded as pending."
                )

            Notification.objects.create(
                user=membership.client.user,
                notification_type=Notification.NotificationType.PAYMENT_RECEIVED,
                title=title,
                message=message,
            )

            return redirect(
                "add_payment",
                membership_id=membership.id,
            )

    else:
        form = PaymentForm()

    total_paid = sum(
        payment.amount
        for payment in membership.payments.all()
        if payment.status in ["PAID", "PARTIAL"]
    )

    amount_due = membership.amount - total_paid

    return render(
        request,
        "accounts/add_payment.html",
        {
            "form": form,
            "membership": membership,
            "total_paid": total_paid,
            "amount_due": amount_due,
        },
    )
def client_memberships(request, client_id):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    from payments.services import sync_membership_statuses

    sync_membership_statuses()

    client = get_object_or_404(ClientProfile, user_id=client_id)

    memberships = list(
        client.memberships
        .prefetch_related("payments")
        .order_by("-start_date")
    )

    client_total_paid = Decimal("0")

    for membership in memberships:
        membership.payment_list = membership.payments.all().order_by(
            "-payment_date"
        )

        membership.total_paid = sum(
            (
                payment.amount
                for payment in membership.payment_list
                if payment.status in ["PAID", "PARTIAL"]
            ),
            Decimal("0"),
        )

        membership.amount_due = membership.amount - membership.total_paid
        client_total_paid += membership.total_paid

    return render(
        request,
        "accounts/client_memberships.html",
        {
            "client": client,
            "memberships": memberships,
            "client_total_paid": client_total_paid,
        },
    )


def revenue_report(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    from django.db.models.functions import TruncMonth, TruncQuarter, TruncYear
    from django.utils import timezone

    paid_payments = Payment.objects.filter(status=Payment.Status.PAID)

    today = timezone.localdate()

    current_month_revenue = paid_payments.filter(
        payment_date__year=today.year,
        payment_date__month=today.month,
    ).aggregate(total=Sum("amount")).get("total") or Decimal("0")

    current_quarter = (today.month - 1) // 3 + 1
    quarter_start_month = 3 * (current_quarter - 1) + 1
    quarter_end_month = quarter_start_month + 2

    current_quarter_revenue = paid_payments.filter(
        payment_date__year=today.year,
        payment_date__month__gte=quarter_start_month,
        payment_date__month__lte=quarter_end_month,
    ).aggregate(total=Sum("amount")).get("total") or Decimal("0")

    current_year_revenue = paid_payments.filter(
        payment_date__year=today.year,
    ).aggregate(total=Sum("amount")).get("total") or Decimal("0")

    total_revenue = paid_payments.aggregate(
        total=Sum("amount")
    ).get("total") or Decimal("0")

    monthly_revenue_qs = (
        paid_payments
        .annotate(period=TruncMonth("payment_date"))
        .values("period")
        .annotate(total=Sum("amount"))
        .order_by("-period")[:12]
    )

    monthly_revenue = [
        {"label": row["period"].strftime("%B %Y"), "total": row["total"]}
        for row in monthly_revenue_qs
    ]

    quarterly_revenue_qs = (
        paid_payments
        .annotate(period=TruncQuarter("payment_date"))
        .values("period")
        .annotate(total=Sum("amount"))
        .order_by("-period")[:8]
    )

    quarterly_revenue = [
        {
            "label": f"Q{((row['period'].month - 1) // 3) + 1} {row['period'].year}",
            "total": row["total"],
        }
        for row in quarterly_revenue_qs
    ]

    yearly_revenue_qs = (
        paid_payments
        .annotate(period=TruncYear("payment_date"))
        .values("period")
        .annotate(total=Sum("amount"))
        .order_by("-period")
    )

    yearly_revenue = [
        {"label": str(row["period"].year), "total": row["total"]}
        for row in yearly_revenue_qs
    ]

    return render(
        request,
        "accounts/revenue_report.html",
        {
            "current_month_revenue": current_month_revenue,
            "current_quarter_revenue": current_quarter_revenue,
            "current_quarter": current_quarter,
            "current_year_revenue": current_year_revenue,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "quarterly_revenue": quarterly_revenue,
            "yearly_revenue": yearly_revenue,
        },
    )
def client_memberships_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "CLIENT":
        return redirect("dashboard")

    from payments.services import sync_membership_statuses

    sync_membership_statuses()

    profile, created = ClientProfile.objects.get_or_create(
        user=request.user
    )

    memberships = list(
        profile.memberships
        .prefetch_related("payments")
        .order_by("-start_date")
    )

    for membership in memberships:
        membership.total_paid = sum(
            (
                payment.amount
                for payment in membership.payments.all()
                if payment.status in ["PAID", "PARTIAL"]
            ),
            Decimal("0"),
        )

        membership.amount_due = membership.amount - membership.total_paid

    return render(
        request,
        "accounts/client_memberships_view.html",
        {
            "profile": profile,
            "memberships": memberships,
        },
    )



def request_otp(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = OTPRequestForm(request.POST)

        if form.is_valid():
            phone = form.cleaned_data["phone"]

            otp = str(random.randint(100000, 999999))

            RegistrationOTP.objects.filter(phone=phone).delete()

            RegistrationOTP.objects.create(
                phone=phone,
                otp=otp,
            )

            request.session["registration_data"] = {
                "first_name": form.cleaned_data["first_name"],
                "last_name": form.cleaned_data["last_name"],
                "email": form.cleaned_data["email"],
                "phone": phone,
            }

            print(f"Longevity+ OTP for {phone}: {otp}")

            return redirect("verify_otp")

    else:
        form = OTPRequestForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


def verify_otp(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    registration_data = request.session.get("registration_data")

    if not registration_data:
        return redirect("register")

    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()

        otp_record = (
            RegistrationOTP.objects
            .filter(phone=registration_data["phone"])
            .order_by("-created_at")
            .first()
        )

        if otp_record is None:
            return render(
                request,
                "accounts/verify_otp.html",
                {"error": "OTP expired or not found."},
            )

        if otp_record.otp != entered_otp:
            otp_record.attempts += 1
            otp_record.save(update_fields=["attempts"])

            return render(
                request,
                "accounts/verify_otp.html",
                {"error": "Invalid OTP. Please try again."},
            )

        # OTP verified
        request.session["otp_verified"] = True

        otp_record.delete()

        return redirect("complete_registration")

    return render(request, "accounts/verify_otp.html")
def complete_registration(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    registration_data = request.session.get("registration_data")
    otp_verified = request.session.get("otp_verified", False)

    if not registration_data or not otp_verified:
        return redirect("register")

    if request.method == "POST":
        form = CompleteRegistrationForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=registration_data["phone"],
                email=registration_data["email"],
                phone=registration_data["phone"],
                first_name=registration_data["first_name"],
                last_name=registration_data["last_name"],
                password=form.cleaned_data["password"],
                role=User.Role.CLIENT,
            )

            # Clear registration session data
            request.session.pop("registration_data", None)
            request.session.pop("otp_verified", None)

            login(request, user)

            return redirect("client_dashboard")

    else:
        form = CompleteRegistrationForm()

    return render(
        request,
        "accounts/complete_registration.html",
        {"form": form},
    )