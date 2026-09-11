from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


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

    return render(request, "accounts/dietitian_dashboard.html")


def client_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "CLIENT":
        return redirect("dashboard")

    return render(request, "accounts/client_dashboard.html")