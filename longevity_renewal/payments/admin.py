from django.contrib import admin

from .models import Membership, MembershipPlan, Payment


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_months", "amount", "country", "is_active", "display_order")
    list_filter = ("country", "is_active")
    ordering = ("display_order", "duration_months")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("client", "name", "amount", "start_date", "end_date", "status", "enrollment")
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("client__user__username", "client__user__email", "name")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("membership", "amount", "payment_date", "payment_method", "status", "transaction_id")
    list_filter = ("status", "payment_method", "payment_date")
    search_fields = ("membership__client__user__username", "transaction_id")
