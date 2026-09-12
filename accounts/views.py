from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from clients.models import ClientProfile
from .forms import ClientProfileForm
from nutrition.models import DietPlan, Meal
from nutrition.forms import DietPlanForm, MealForm
from progress.forms import ProgressRecordForm
from progress.models import ProgressRecord
from payments.forms import MembershipForm, PaymentForm
from payments.models import Membership


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        return render(
            request,
            "accounts/login.html",
            {
                "error": "Invalid username or password."
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

    return render(request, "accounts/admin_dashboard.html")


def dietitian_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "DIETITIAN":
        return redirect("dashboard")

    from accounts.models import User

    clients = (
        User.objects
        .filter(role="CLIENT")
        .prefetch_related(
            "client_profile__memberships"
        )
        .order_by("first_name", "last_name")
    )

    return render(
        request,
        "accounts/dietitian_dashboard.html",
        {
            "clients": clients,
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

    return render(
        request,
        "accounts/client_dashboard.html",
        {
            "profile": profile,
            "active_diet_plan": active_diet_plan,
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

    client = ClientProfile.objects.get(
        user_id=client_id
    )

    if request.method == "POST":
        form = DietPlanForm(request.POST)

        if form.is_valid():
            diet_plan = form.save(commit=False)
            diet_plan.client = client.user
            diet_plan.save()

            return redirect(
                "add_meal",diet_plan_id=diet_plan.id,
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

    client = ClientProfile.objects.get(
        user_id=client_id
    )

    if request.method == "POST":
        form = ProgressRecordForm(request.POST)

        if form.is_valid():
            progress = form.save(commit=False)
            progress.client = client
            progress.save()

            return redirect(
                "add_progress",
                client_id=client.id,
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

    client = ClientProfile.objects.get(
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