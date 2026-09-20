from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from clients.models import ClientProfile
from notifications.models import Notification
from payments.models import Membership

from .forms import QueryForm, QueryMessageForm
from .models import Query, QueryMessage


def _active_membership(profile):
    from payments.services import sync_membership_statuses
    sync_membership_statuses()
    return profile.memberships.filter(status=Membership.Status.ACTIVE).order_by("-end_date").first()


def _ensure_dietitian(profile):
    if profile.assigned_dietitian_id:
        return profile.assigned_dietitian
    dietitian = User.objects.filter(role=User.Role.DIETITIAN).order_by("id").first()
    if dietitian:
        profile.assigned_dietitian = dietitian
        profile.save(update_fields=["assigned_dietitian"])
    return dietitian


def _notify(user, title, message):
    Notification.objects.create(
        user=user,
        notification_type=Notification.NotificationType.GENERAL,
        title=title,
        message=message,
    )


@login_required
def client_queries(request):
    if request.user.role != User.Role.CLIENT:
        return redirect("dashboard")
    profile = get_object_or_404(ClientProfile, user=request.user)
    active_membership = _active_membership(profile)
    if not profile.memberships.exists() and not Query.objects.filter(client=profile).exists():
        return redirect("client_dashboard")
    queries = Query.objects.filter(client=profile).select_related("dietitian", "membership")
    return render(request, "queries/client_queries.html", {
        "queries": queries,
        "active_membership": active_membership,
        "can_create": active_membership is not None,
    })


@login_required
def create_query(request):
    if request.user.role != User.Role.CLIENT:
        return redirect("dashboard")
    profile = get_object_or_404(ClientProfile, user=request.user)
    membership = _active_membership(profile)
    if not membership:
        if Query.objects.filter(client=profile).exists():
            return redirect("client_queries")
        return redirect("client_dashboard")
    dietitian = _ensure_dietitian(profile)
    if not dietitian:
        return render(request, "queries/no_dietitian.html")
    if request.method == "POST":
        form = QueryForm(request.POST)
        message_form = QueryMessageForm(request.POST)
        if form.is_valid() and message_form.is_valid():
            query = form.save(commit=False)
            query.client = profile
            query.membership = membership
            query.dietitian = dietitian
            query.status = Query.Status.OPEN
            query.save()
            QueryMessage.objects.create(query=query, sender=request.user, message=message_form.cleaned_data["message"])
            _notify(dietitian, "New Client Query", f"{profile} submitted: {query.subject}")
            return redirect("query_detail", query_id=query.id)
    else:
        form = QueryForm()
        message_form = QueryMessageForm()
    return render(request, "queries/create_query.html", {"form": form, "message_form": message_form})


@login_required
def query_detail(request, query_id):
    query = get_object_or_404(Query.objects.select_related("client__user", "dietitian", "membership"), id=query_id)
    is_client = request.user.role == User.Role.CLIENT and query.client.user_id == request.user.id
    is_dietitian = request.user.role == User.Role.DIETITIAN and query.dietitian_id == request.user.id
    if not (is_client or is_dietitian):
        return redirect("dashboard")
    if request.method == "POST":
        if is_client and _active_membership(query.client) is None:
            return redirect("client_queries")
        form = QueryMessageForm(request.POST)
        if form.is_valid():
            QueryMessage.objects.create(query=query, sender=request.user, message=form.cleaned_data["message"])
            if is_client:
                if query.status == Query.Status.CLOSED:
                    query.status = Query.Status.OPEN
                _notify(query.dietitian, "New Query Message", f"{query.client} replied to: {query.subject}")
            else:
                if query.status in {Query.Status.OPEN, Query.Status.ANSWERED}:
                    query.status = Query.Status.IN_PROGRESS
                _notify(query.client.user, "Dietitian Replied", f"Your query has a new response: {query.subject}")
            query.save(update_fields=["status", "updated_at"])
            return redirect("query_detail", query_id=query.id)
    else:
        form = QueryMessageForm()
    return render(request, "queries/query_detail.html", {
        "query": query,
        "messages": query.messages.select_related("sender"),
        "form": form,
        "is_client": is_client,
    })


@login_required
def update_query_status(request, query_id):
    if request.user.role != User.Role.DIETITIAN:
        return redirect("dashboard")
    query = get_object_or_404(Query, id=query_id, dietitian=request.user)
    if request.method == "POST":
        status = request.POST.get("status")
        if status in Query.Status.values:
            query.status = status
            query.save(update_fields=["status", "updated_at"])
            _notify(query.client.user, "Query Status Updated", f"Your query '{query.subject}' is now {query.get_status_display()}.")
    return redirect("query_detail", query_id=query.id)


@login_required
def dietitian_queries(request):
    if request.user.role != User.Role.DIETITIAN:
        return redirect("dashboard")
    queries = Query.objects.filter(dietitian=request.user).select_related("client__user").annotate(message_count=Count("messages"))
    status = request.GET.get("status")
    if status in Query.Status.values:
        queries = queries.filter(status=status)
    return render(request, "queries/dietitian_queries.html", {
        "queries": queries,
        "status_filter": status,
        "open_count": Query.objects.filter(dietitian=request.user, status=Query.Status.OPEN).count(),
        "in_progress_count": Query.objects.filter(dietitian=request.user, status=Query.Status.IN_PROGRESS).count(),
        "answered_count": Query.objects.filter(dietitian=request.user, status=Query.Status.ANSWERED).count(),
    })
